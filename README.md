# proxy-minimal — Reverse Proxy شفاف مثل alwaysdata

فقط یک خط تنظیم دارد: آدرس مقصد. کلید، پروایدر، مدل، Rate Limit، احراز هویت —
هیچ‌کدام در این پروکسی نیست و وارد نمی‌شود.

## تنظیم (فقط همین یک خط)

`.env.example` را کپی کن به `.env` و آدرس را بنویس:

```
TARGET_BASE_URL=https://api.example.com:8080
```

## اجرا

```bash
pip install -r requirements.txt
uvicorn proxy:app --host 0.0.0.0 --port 3000
```

یا با Docker:

```bash
docker compose up --build -d
curl http://localhost:8000/health
```

## چه کار می‌کند

```
کلاینت -> http://localhost:3000/v1/models?x=1
       -> https://api.example.com:8080/v1/models?x=1
```

- متد، مسیر، query، بدنه و هدرها دقیقاً همان‌طور که رسیده‌اند رد می‌شوند.
- جواب با همان status و همان بایت‌ها برمی‌گردد (استریم/SSE هم سالم می‌ماند).
- اگر کلاینت خودش هدر `Authorization` بفرستد، همان‌طور رد می‌شود؛
  پروکسی کلیدی نمی‌داند، اضافه نمی‌کند و ذخیره نمی‌کند.
- تنها مسیر اضافه `/health` است که می‌گوید پروکسی بالاست و مقصد چیست.

## اگر واقعاً روی alwaysdata هستی

آنجا اصلاً به این کد نیاز نداری؛ خود پنل همین کار را می‌کند:
Websites → Add site → نوع Reverse Proxy → دامنه خودت → آدرس مقصد.
این کد برای وقتی است که همان رفتار را روی سرور خودت (VPS و...) می‌خواهی.

## کجا اجرا کنم؟ (جایگزین alwaysdata)

این کد یک سرور دائمی است؛ روی Vercel و Netlify و Cloudflare Workers اجرا
**نمی‌شود** (آن‌ها Serverless/JS هستند، نه سرور Python دائمی).

- **روی کامپیوتر خودت (تست):** `pip install -r requirements.txt` بعد
  `TARGET_BASE_URL=https://... uvicorn proxy:app --port 3000` و تست
  `http://localhost:3000/health`.
- **روی VPS با Docker:** فایل `.env` را با `TARGET_BASE_URL` بساز و
  `docker compose up --build -d`.
- **Koyeb (پیشنهاد اول برای جایگزین):** پوشه را در یک ریپوی GitHub بگذار،
  در Koyeb گزینه Create App → Deploy from GitHub → Builder: Dockerfile،
  و در Environment variables فقط `TARGET_BASE_URL` را ست کن. پلن Starter
  رایگان است: یک سرویس ۵۱۲ مگابایت/0.1 vCPU، فقط Frankfurt یا Washington؛
  بعد از یک ساعت بی‌کاری خاموش می‌شود و اولین درخواست بعدی کمی دیر جواب
  می‌دهد. منابع جدید می‌گویند موقع ثبت‌نام کارت می‌خواهد (با هولد ۲۹ دلاری)؛
  موقع ثبت‌نام خودش را چک کن.
- **Railway / Render:** مثل Koyeb از روی GitHub و Dockerfile بالا می‌آید و
  فقط `TARGET_BASE_URL` را می‌خواهد؛ Render رایگان بعد از ۱۵ دقیقه بی‌کاری
  می‌خوابد. Railway اعتبار آزمایشی می‌دهد و بعد پولی است.
- **روی خود alwaysdata:** با همین فایل هم می‌شود (سایت Python، فایل
  `proxy.py` و متغیر `TARGET_BASE_URL`)، ولی اگر همان‌جا هستی اصلاً به کد
  نیاز نداری؛ پنل خودش Reverse Proxy دارد.

## تفاوت با نسخه proxy-fixed

| | proxy-minimal (این پوشه) | proxy-fixed |
|---|---|---|
| تنظیم | فقط آدرس مقصد | آدرس + کلید به‌ازای هر پروایدر |
| کلید | پروکسی کلید نمی‌داند | پروکسی کلید را تزریق می‌کند |
| احراز هویت تماس‌گیرنده | ندارد | `X-Proxy-Key` اختیاری |
| Rate Limit | ندارد | دارد |
| مناسب برای | مقصدی که کلید نمی‌خواهد، یا کلاینت خودش کلید می‌فرستد | پنهان کردن کلید از کلاینت |
