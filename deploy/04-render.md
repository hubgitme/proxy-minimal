# ۴ — استقرار روی Render

## چه لازم داری
- یک حساب GitHub و یک حساب Render.
- پوشه `proxy-minimal` را در یک ریپوی GitHub بگذار (ریپو باید `proxy.py` و
  `Dockerfile` و `requirements.txt` را در ریشه داشته باشد).

## قدم‌ها

### ۱) سرویس بساز
1. وارد Render شو → **New** → **Web Service**.
2. **Build and deploy from a Git repository** را انتخاب کن و ریپو را انتخاب کن.
3. **Runtime** را **Docker** بگذار و مسیر Dockerfile را ریشه بگذار.
4. **Instance Type** را **Free** انتخاب کن.

### ۲) فقط یک متغیر محیطی ست کن
در بخش **Environment Variables** همان سرویس:

```
TARGET_BASE_URL=https://آدرس-مقصد-خودت
```

پورت را Render خودش با `PORT` ست می‌کند و Dockerfile همین را می‌خواند.

### ۳) Health Check (اختیاری ولی خوب است)
در تنظیمات سرویس، **Health Check Path** را `/health` بگذار تا Render خودش
بفهمد سرویس بالاست.

### ۴) Deploy و تست
- **Create Web Service** را بزن و صبر کن تا وضعیت Live شود.
- آدرس سرویس چیزی شبیه این می‌شود: `https://نام-سرویس.onrender.com`
- اول تست سلامت:
  ```
  https://نام-سرویس.onrender.com/health
  ```
- بعد یک مسیر واقعی، مثلاً `/v1/models` — باید جواب مقصد برگردد.

## نکات مهم
- **پلن رایگان و خوابیدن:** سرویس رایگان بعد از ۱۵ دقیقه بی‌کاری خاموش
  می‌شود و درخواست بعدی حدود یک دقیقه طول می‌کشد تا سرویس دوباره بالا بیاید.
  برای تست خوب است؛ برای استفاده دائمی و فوری، VPS (فایل ۰۵) بهتر است.
- **تغییر مقصد:** فقط مقدار `TARGET_BASE_URL` را در Environment Variables
  عوض کن و **Manual Deploy** → **Deploy latest commit** را بزن.
- **به‌روزرسانی کد:** هر push جدید به branch، خودش دوباره Deploy می‌شود
  (اگر Auto-Deploy روشن باشد).
- **بیلد رایگان کند است:** اولین بیلد چند دقیقه طول می‌کشد؛ طبیعی است.
