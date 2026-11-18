# ریورس پروکسی شفاف چندپروایدره

مثل Reverse Proxy پنل alwaysdata، ولی با چند مقصد. برای هر پروایدر فقط
**آدرس** را وارد می‌کنی؛ نه کلید، نه مدل، نه هیچ چیز دیگر.

## پروایدرها را چطور تعریف می‌کنی

برای هر پروایدر یک متغیر محیطی با اسم دلخواه خودت:

```env
GROQ_BASE_URL=https://api.groq.com/openai/v1
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

مسیرها (نام در URL کوچک می‌شود):

```text
POST /groq/chat/completions       ->  https://api.groq.com/openai/v1/chat/completions
POST /openrouter/chat/completions ->  https://openrouter.ai/api/v1/chat/completions
```

کلید را پروکسی نمی‌داند و تزریق نمی‌کند؛ اگر مقصد کلید بخواهد، خود
کلاینت آن را در هدر `Authorization` می‌فرستد، مثل وقتی که مستقیم وصل می‌شد.

## مسیرهای خود پروکسی

- `GET /health` — وضعیت و لیست پروایدرهای تعریف‌شده
- `GET /` — لیست پروایدرهای تعریف‌شده
- `GET /<name>/...` — هر چیز دیگر به آدرس همان پروایدر رد می‌شود

پروایدر ناشناخته 404 می‌دهد و لیست پروایدرهای موجود را نشان می‌دهد.

## اجرای لوکال

```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
set GROQ_BASE_URL=https://api.groq.com/openai/v1
uvicorn proxy:app --port 3000
```

بعد `http://localhost:3000/health` را باز کن.

## دیپلوی

مثل نسخه تک‌پروایدره: ریپو را به Koyeb بده (Builder روی Dockerfile)،
و برای هر پروایدر یک متغیر محیطی `<NAME>_BASE_URL` در پنل ست کن.
فقط یک نکته: آدرس سرویس عوض می‌شود و مسیرها `/<name>/...` هستند،
پس در کلاینتت هم باید آدرس پایه و مسیر را به همین شکل به‌روز کنی.
