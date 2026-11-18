# ۱ — اجرا روی کامپیوتر خودت (ویندوز، فقط برای تست)

## چه لازم داری
- Python 3.11 یا بالاتر نصب‌شده باشد (`python --version` در PowerShell).
- پوشه `proxy-minimal` (همان زیپ را باز کن).

## قدم‌ها

### ۱) محیط مجازی و نصب
در PowerShell، داخل پوشه `proxy-minimal`:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### ۲) آدرس مقصد را ست کن
فقط همین یک خط — آدرس مقصد خودت را به‌جای مثال بگذار:

```powershell
$env:TARGET_BASE_URL="https://api.example.com:8080"
```

### ۳) اجرا
```powershell
uvicorn proxy:app --host 0.0.0.0 --port 3000
```

### ۴) تست
در مرورگر یا یک PowerShell دیگر:

```powershell
Invoke-WebRequest http://localhost:3000/health
```

باید `{"status":"ok","target":"https://api.example.com:8080"}` برگردد.
بعد یک مسیر واقعی را تست کن، مثلاً:

```
http://localhost:3000/v1/models
```

باید همان جوابی برگردد که مقصد مستقیم می‌دهد.

## توقف
در همان پنجره `Ctrl+C` بزن.

## محدودیت
فقط از روی همین کامپیوتر در دسترس است؛ برای اینکه دیگران هم به آن برسند باید
روی یک هاست اجرا شود (فایل‌های ۰۲ تا ۰۶). اگر پنجره بسته شود یا کامپیوتر
خاموش شود، پروکسی هم قطع می‌شود.
