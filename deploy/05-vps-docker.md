# ۵ — استقرار روی VPS خودت با Docker

## چه لازم داری
- یک VPS لینوکسی با Docker و Docker Compose نصب‌شده.
- زیپ `proxy-minimal` را روی سرور باز کن.

## قدم‌ها

### ۱) فایل‌ها را روی سرور بگذار
```bash
unzip proxy-minimal.zip
cd proxy-minimal
```

### ۲) فقط آدرس مقصد را بنویس
فایل `.env` را بساز (فقط همین یک خط):

```bash
cp .env.example .env
nano .env
```

داخلش:
```
TARGET_BASE_URL=https://آدرس-مقصد-خودت
```

### ۳) اجرا
```bash
docker compose up --build -d
```

### ۴) تست
```bash
docker compose ps
docker compose logs -f reverse-proxy
curl http://localhost:8000/health
```

باید `{"status":"ok",...}` برگردد. بعد از بیرون سرور تست کن:
```
http://IP-سرور:8000/v1/models
```

### ۵) اگر می‌خواهی با دامنه و HTTPS باشد
پورت ۸۰۰۰ را مستقیم باز نکن؛ جلویش یک وب‌سرور (Caddy یا Nginx) بگذار که
دامنه‌ات را به `localhost:8000` وصل کند و خودش HTTPS بدهد. این بخش جدا از
پروکسی است و به تنظیمات دامنه خودت بستگی دارد.

## نگهداری
- **تغییر مقصد:** مقدار `TARGET_BASE_URL` را در `.env` عوض کن و بزن:
  ```bash
  docker compose up -d
  ```
- **به‌روزرسانی کد:** فایل‌های جدید را جایگزین کن و بزن:
  ```bash
  docker compose up --build -d
  ```
- **توقف:**
  ```bash
  docker compose down
  ```

## نکته مهم
برخلاف پلن‌های رایگان Koyeb و Render، اینجا سرویس نمی‌خوابد و همیشه روشن
می‌ماند؛ به‌شرط اینکه VPS روشن باشد. هزینه‌اش همان هزینه VPS است.
