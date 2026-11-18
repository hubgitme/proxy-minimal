# proxy.py — Reverse Proxy شفافِ چندپروایدره، مثل Reverse Proxy پنل alwaysdata
#
# همان مدل شفاف نسخه مینیمال، ولی با چند مقصد:
# برای هر پروایدر فقط «آدرس» را می‌دهی — نه کلید، نه مدل، نه هیچ چیز دیگر.
# پروایدرها را خودت تعیین می‌کنی و دستی در متغیرهای محیطی می‌نویسی؛
# اسم را هم خودت انتخاب می‌کنی (GROQ فقط مثال است):
#
#   GROQ_BASE_URL=https://api.groq.com/openai/v1
#   OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
#
# آن‌وقت مسیر این می‌شود (نام در URL کوچک می‌شود):
#   POST /groq/chat/completions       ->  https://api.groq.com/openai/v1/chat/completions
#   POST /openrouter/chat/completions ->  https://openrouter.ai/api/v1/chat/completions
#
# هیچ کلیدی در پروکسی نیست و هیچ کلیدی تزریق نمی‌شود:
# هدرها (از جمله Authorization خود کلاینت، اگر فرستاده باشد)، بدنه،
# متد، مسیر و query دقیقاً همان‌طور که رسیده‌اند رد می‌شوند؛
# جواب هم با همان status و همان بایت‌ها برمی‌گردد.
# اگر مقصد کلید بخواهد، خود کلاینت باید آن را در هدرش بفرستد،
# مثل وقتی که مستقیم وصل می‌شد.
#
# برای اضافه کردن پروایدر، فقط یک خط <NAME>_BASE_URL اضافه کن؛
# برای حذف، همان خط را بردار و سرویس را ری‌استارت کن.
#
# اجرا:
#   pip install -r requirements.txt
#   GROQ_BASE_URL=https://api.groq.com/openai/v1 uvicorn proxy:app --host 0.0.0.0 --port 3000

import os
import re

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

# پروایدرها فقط از آدرس خوانده می‌شوند: هر متغیر <NAME>_BASE_URL یک پروایدر است.
# NAME همان چیزی است که تو نوشته‌ای؛ در مسیر، کوچک می‌شود.
_PROVIDERS: dict[str, str] = {}
for _key, _value in os.environ.items():
    _m = re.fullmatch(r"([A-Za-z0-9_]+)_BASE_URL", _key)
    if _m and _value.strip():
        _PROVIDERS[_m.group(1).lower()] = _value.strip().rstrip("/")

app = FastAPI(title="Reverse Proxy (transparent, multi-provider)")


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
    # فقط برای اینکه بفهمی پروکسی بالاست و کدام پروایدرها تعریف شده‌اند.
    return {"status": "ok", "providers": sorted(_PROVIDERS.keys())}


@app.get("/")
async def index():
    # لیست پروایدرهای تعریف‌شده؛ چیز دیگری اینجا نیست.
    return {"providers": sorted(_PROVIDERS.keys())}


@app.api_route(
    "/{name}/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
)
async def reverse_proxy(name: str, path: str, request: Request):
    base = _PROVIDERS.get(name.lower())
    if base is None:
        return JSONResponse(
            status_code=404,
            content={
                "error": f"Unknown provider: {name}",
                "providers": sorted(_PROVIDERS.keys()),
            },
        )

    url = f"{base}/{path}"
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
