# proxy.py — Reverse Proxy شفاف، مثل Reverse Proxy پنل alwaysdata
#
# ریورس پروکسی یعنی: یک سرور واسط که جلوی سرور اصلی می‌ایستد.
# کلاینت به آدرس پروکسی وصل می‌شود، پروکسی درخواست را همان‌طور که هست
# به سرور مقصد می‌فرستد و جواب را همان‌طور که هست برمی‌گرداند.
# کلاینت اصلاً سرور مقصد را نمی‌بیند؛ فقط آدرس پروکسی را می‌بیند.
#
# مثل پنل alwaysdata: آنجا هم فقط «آدرس مقصد» را می‌دهی، نه کلید،
# نه پروایدر، نه مدل، نه هیچ چیز دیگر. اینجا هم دقیقاً همان است —
# تنها چیزی که وارد می‌کنی، یک خط است:
#
#   TARGET_BASE_URL=https://آدرس-مقصد
#
# مثال:
#   TARGET_BASE_URL=https://api.example.com:8080
# آن‌وقت:
#   GET  http://localhost:3000/v1/models
#   ->   GET https://api.example.com:8080/v1/models
#
# پروکسی هیچ‌چیز به درخواست اضافه یا از آن کم نمی‌کند:
# هدرها (از جمله Authorization خود کلاینت، اگر فرستاده باشد)، بدنه،
# متد، مسیر و query دقیقاً همان‌طور که رسیده‌اند رد می‌شوند؛
# جواب هم با همان status و همان بایت‌ها برمی‌گردد.
# کلید را پروکسی نمی‌داند و نمی‌فرستد؛ اگر مقصد کلید بخواهد،
# خود کلاینت باید آن را در هدرش بفرستد، مثل وقتی که مستقیم وصل می‌شد.
#
# اجرا:
#   pip install -r requirements.txt
#   TARGET_BASE_URL=https://آدرس-مقصد uvicorn proxy:app --host 0.0.0.0 --port 3000

import os

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

# تنها تنظیم: آدرس مقصد. چیز دیگری برای وارد کردن نیست.
TARGET_BASE_URL = os.getenv("TARGET_BASE_URL", "").strip().rstrip("/")

app = FastAPI(title="Reverse Proxy (transparent)")


# هدرهای hop-by-hop که نباید رد شوند؛ بقیه هدرها دست‌نخورده می‌مانند.
_HOP_HEADERS = {
    "host",
    "content-length",
    "transfer-encoding",
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "upgrade",
}


@app.get("/health")
async def health():
    # تنها مسیر اضافه؛ فقط برای اینکه بفهمی پروکسی بالاست.
    return {"status": "ok", "target": TARGET_BASE_URL or "not configured"}


@app.api_route(
    "/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]
)
async def reverse_proxy(path: str, request: Request):
    if not TARGET_BASE_URL:
        return JSONResponse(
            status_code=503,
            content={"error": "TARGET_BASE_URL is not set"},
        )

    url = f"{TARGET_BASE_URL}/{path}"
    if request.url.query:
        url += f"?{request.url.query}"

    # هدرهای کلاینت همان‌طور که هستند؛ هیچ هدری اضافه یا حذف نمی‌شود
    # (به‌جز hop-by-hop که مال خود اتصال است، نه درخواست).
    headers = {
        k: v for k, v in request.headers.items() if k.lower() not in _HOP_HEADERS
    }
    body = await request.body() if request.method not in ("GET", "HEAD") else None

    client = httpx.AsyncClient(timeout=httpx.Timeout(300.0), follow_redirects=False)
    try:
        req = client.build_request(request.method, url, headers=headers, content=body)
        upstream = await client.send(req, stream=True)
    except httpx.TimeoutException:
        await client.aclose()
        return JSONResponse(status_code=504, content={"error": "Upstream timeout"})
    except httpx.RequestError as exc:
        await client.aclose()
        return JSONResponse(status_code=502, content={"error": f"Upstream error: {exc}"})

    async def event_stream():
        try:
            async for chunk in upstream.aiter_bytes():
                yield chunk
        finally:
            await upstream.aclose()
            await client.aclose()

    resp_headers = {
        k: v for k, v in upstream.headers.items() if k.lower() not in _HOP_HEADERS
    }
    resp_headers.pop("content-encoding", None)  # چون aiter_bytes دیکد شده تحویل می‌دهد
    return StreamingResponse(
        event_stream(),
        status_code=upstream.status_code,
        headers=resp_headers,
        media_type=upstream.headers.get("content-type"),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "3000")))
