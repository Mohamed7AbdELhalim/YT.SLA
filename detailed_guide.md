# دليل شامل لأداة أرشفة فيديوهات يوتيوب 🎥📦

## المحتويات
1. [نظرة عامة على الأداة](#نظرة-عامة-على-الأداة)
2. [شرح مفصل للكود مع تعليقات](#شرح-مفصل-للكود-مع-تعليقات)
3. [ميزات الأداة](#ميزات-الأداة)
4. [أمثلة الاستخدام](#أمثلة-الاستخدام)
5. [نصائح وحلول للمشاكل](#نصائح-وحلول-للمشاكل)

---

## نظرة عامة على الأداة

هذه أداة بايثون مصممة خصيصاً لأرشفة عدد كبير من فيديوهات يوتيوب (مئات أو آلاف الفيديوهات)، مشابهة للأداة التي استخدمتها لأرشفة 1200+ فيديو.

### المكتبات المستخدمة
- **yt-dlp**: أقوى أداة لتحميل الفيديوهات من يوتيوب وأكثر من 1000 موقع آخر
- **concurrent.futures**: للتحميل المتوازي (عدة فيديوهات في نفس الوقت)
- **argparse**: لمعالجة خيارات سطر الأوامر
- **pathlib**: للتعامل مع المسارات بطريقة حديثة وآمنة

---

## شرح مفصل للكود مع تعليقات

### القسم 1️⃣: استيراد المكتبات والإعدادات الأولية

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# السطر الأول: يخبر نظام التشغيل أن هذا سكربت بايثون 3
# السطر الثاني: يحدد ترميز الملف UTF-8 لدعم العربية والحروف الخاصة

"""
docstring متعدد الأسطر يشرح الأداة بالكامل
يمكن الوصول إليه عبر:
  python youtube_archiver.py --help
"""

import argparse          # لمعالجة الخيارات من سطر الأوامر (--urls-file, --output-dir, إلخ)
import concurrent.futures # للتحميل المتوازي (تحميل عدة فيديوهات في آن واحد)
import datetime as dt    # للحصول على التاريخ والوقت الحالي للسجلات
import os                # للتعامل مع نظام الملفات (نادر الاستخدام هنا)
import sys               # للتحكم في إنهاء البرنامج والوصول إلى معاملات النظام
from pathlib import Path # طريقة حديثة للتعامل مع المسارات (أفضل من os.path)

try:
    from yt_dlp import YoutubeDL  # استيراد المكتبة الرئيسية للتحميل
except ImportError:
    # إذا لم تكن المكتبة مثبتة، نطبع رسالة واضحة ونخرج
    print("[!] مكتبة yt-dlp غير مثبتة. ثبّتها بالأمر:")
    print("    pip install yt-dlp")
    sys.exit(1)  # الخروج برمز خطأ 1
```

---

### القسم 2️⃣: دالة السجلات (Logging)

```python
def log(message: str, *, log_file: Path | None = None) -> None:
    """
    دالة لطباعة رسالة على الشاشة وحفظها في ملف السجل
    
    المعاملات:
        message: النص المراد طباعته وحفظه
        log_file: مسار ملف السجل (اختياري)
    
    العودة:
        None (لا ترجع شيئاً)
    """
    # الحصول على التاريخ والوقت الحالي بصيغة: 2024-01-15 14:30:45
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # تنسيق السطر: [2024-01-15 14:30:45] الرسالة هنا
    line = f"[{now}] {message}"
    
    # طباعة على الشاشة (stdout)
    print(line)
    
    # إذا تم تحديد ملف سجل، نحفظ الرسالة فيه
    if log_file is not None:
        # إنشاء المجلدات إذا لم تكن موجودة
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # فتح الملف في وضع الإضافة (append) وليس الكتابة (write)
        # حتى لا نمسح السجلات السابقة
        with log_file.open("a", encoding="utf-8") as f:
            f.write(line + "\n")  # كتابة السطر مع سطر جديد
```

**فائدة هذه الدالة:**
- توحيد طريقة السجلات في كل البرنامج
- الحفاظ على سجل دائم للعمليات (مفيد جداً عند أرشفة 1000+ فيديو)
- إضافة timestamp تلقائي لكل عملية

---

### القسم 3️⃣: قراءة الروابط من الملف

```python
def load_urls(urls_path: Path) -> list[str]:
    """
    قراءة الروابط من ملف نصي
    
    المعاملات:
        urls_path: مسار ملف الروابط (urls.txt)
    
    العودة:
        قائمة (list) من الروابط النظيفة
    
    الاستثناءات:
        FileNotFoundError: إذا كان الملف غير موجود
    """
    # التحقق من وجود الملف قبل القراءة
    if not urls_path.exists():
        raise FileNotFoundError(f"ملف الروابط غير موجود: {urls_path}")
    
    # قائمة فارغة لحفظ الروابط
    urls: list[str] = []
    
    # فتح الملف بترميز UTF-8 (مهم للروابط العربية)
    with urls_path.open("r", encoding="utf-8") as f:
        # قراءة كل سطر في الملف
        for line in f:
            line = line.strip()  # إزالة المسافات والأسطر الجديدة من البداية والنهاية
            
            # تجاهل السطور الفارغة والتعليقات (التي تبدأ بـ #)
            if not line or line.startswith("#"):
                continue  # الانتقال للسطر التالي
            
            # إضافة الرابط إلى القائمة
            urls.append(line)
    
    # إرجاع قائمة الروابط
    return urls
```

**ملاحظات مهمة:**
- يدعم التعليقات في ملف الروابط (أي سطر يبدأ بـ `#`)
- يتجاهل السطور الفارغة تلقائياً
- يمكنك تنظيم الملف بسهولة:
  ```
  # فيديوهات تعليمية
  https://youtube.com/watch?v=abc123
  https://youtube.com/watch?v=def456
  
  # قائمة تشغيل المفضلة
  https://youtube.com/playlist?list=xyz789
  ```

---

### القسم 4️⃣: إعداد خيارات yt-dlp

```python
def build_ydl_opts(output_dir: Path, fmt: str) -> dict:
    """
    بناء القاموس (dictionary) الذي يحتوي على جميع إعدادات yt-dlp
    
    المعاملات:
        output_dir: مجلد حفظ الفيديوهات
        fmt: صيغة التحميل (مثل: bestvideo+bestaudio)
    
    العودة:
        قاموس (dict) يحتوي على الإعدادات
    """
    
    # ==== 1. تحديد نمط اسم الملف الناتج ====
    # %(uploader)s = اسم صاحب القناة
    # %(upload_date)s = تاريخ الرفع بصيغة YYYYMMDD
    # %(title)s = عنوان الفيديو
    # %(id)s = معرّف الفيديو الفريد
    # %(ext)s = امتداد الملف (mp4, webm, إلخ)
    outtmpl = str(output_dir / "%(uploader)s/%(upload_date)s - %(title)s [%(id)s].%(ext)s")
    
    # مثال للملف الناتج:
    # archive/TechChannel/20240115 - كيفية البرمجة [abc123xyz].mp4
    
    # ==== 2. بناء قاموس الإعدادات ====
    ydl_opts: dict = {
        # مسار وتنسيق اسم الملف الناتج
        'outtmpl': outtmpl,
        
        # صيغة التحميل:
        # - bestvideo+bestaudio: أعلى جودة فيديو + أعلى جودة صوت ثم دمجهما
        # - best: أفضل جودة متاحة (فيديو+صوت معاً)
        'format': fmt,
        
        # السماح بتحميل قوائم التشغيل (False تعني السماح، اسم خادع!)
        'noplaylist': False,
        
        # عدم التوقف إذا فشل فيديو واحد في قائمة تشغيل
        # مفيد جداً عند أرشفة مئات الفيديوهات
        'ignoreerrors': True,
        
        # عدد محاولات إعادة التحميل إذا فشل الاتصال
        'retries': 5,
        
        # عدد محاولات إعادة تحميل الأجزاء (fragments) المفقودة
        'fragment_retries': 10,
        
        # عدد الأجزاء التي يتم تحميلها في نفس الوقت (تسريع التحميل)
        'concurrent_fragment_downloads': 5,
        
        # دمج الفيديو والصوت في ملف MP4 واحد
        'merge_output_format': 'mp4',
        
        # استكمال التحميل إذا توقف في منتصفه (Resume)
        # مفيد جداً للفيديوهات الكبيرة
        'continuedl': True,
        
        # إظهار شريط التقدم أثناء التحميل
        'noprogress': False,
        
        # تعطيل logger الخاص بـ yt-dlp (يمكنك استبداله بـ logger مخصص)
        'logger': None,
        
        # إظهار الرسائل (False = إظهار، True = إخفاء)
        'quiet': False,
        
        # ==== إعدادات إضافية للميتاداتا (يتم إضافتها إذا اخترت ذلك) ====
        # 'writeinfojson': True,        # حفظ معلومات الفيديو في ملف JSON
        # 'writesubtitles': True,        # تحميل الترجمات اليدوية
        # 'writeautomaticsub': True,     # تحميل الترجمات التلقائية
        # 'writethumbnail': True,        # تحميل الصورة المصغرة
    }
    
    # إرجاع القاموس
    return ydl_opts
```

**ملاحظات مهمة:**
- `outtmpl` يحدد كيف يتم تنظيم الملفات في مجلدات
- `ignoreerrors=True` **ضروري جداً** عند أرشفة عدد كبير من الفيديوهات
- `continuedl=True` يوفر الكثير من الوقت إذا انقطع الإنترنت

---

### القسم 5️⃣: تحميل فيديو واحد

```python
def download_one(index: int, url: str, output_dir: Path, fmt: str, log_file: Path) -> None:
    """
    تحميل فيديو واحد أو قائمة تشغيل كاملة
    
    المعاملات:
        index: رقم الفيديو في القائمة (للسجلات)
        url: رابط الفيديو أو قائمة التشغيل
        output_dir: مجلد الحفظ
        fmt: صيغة التحميل
        log_file: ملف السجل
    
    العودة:
        None
    """
    try:
        # تسجيل بداية التحميل
        log(f"[{index}] بدء التحميل: {url}", log_file=log_file)
        
        # بناء الإعدادات
        ydl_opts = build_ydl_opts(output_dir, fmt)
        
        # استخدام YoutubeDL context manager (with statement)
        # يضمن إغلاق الاتصالات بشكل صحيح حتى لو حدث خطأ
        with YoutubeDL(ydl_opts) as ydl:
            # تحميل الفيديو/القائمة
            # download() تقبل قائمة من الروابط
            ydl.download([url])
        
        # تسجيل نجاح العملية
        log(f"[{index}] تم التحميل بنجاح", log_file=log_file)
        
    except Exception as e:
        # في حالة حدوث أي خطأ، نسجله ونستمر
        # لا نريد أن يتوقف البرنامج كله بسبب فيديو واحد
        log(f"[{index}] فشل التحميل: {url} | الخطأ: {e}", log_file=log_file)
```

**الأخطاء الشائعة وحلولها:**
- `Video unavailable`: الفيديو محذوف أو خاص
- `HTTP Error 429`: تم حظرك مؤقتاً، قلل عدد التحميلات المتوازية
- `Unable to extract`: مشكلة في parsing، حدّث yt-dlp

---

### القسم 6️⃣: الدالة الرئيسية (main)

```python
def main() -> None:
    """
    الدالة الرئيسية التي تدير كل شيء
    """
    
    # ==== 1. إنشاء parser لمعالجة خيارات سطر الأوامر ====
    parser = argparse.ArgumentParser(description="أداة أرشفة يوتيوب")
    
    # إضافة خيار --urls-file
    # default: القيمة الافتراضية إذا لم يحدد المستخدم
    # help: النص الذي يظهر في --help
    parser.add_argument("--urls-file", 
                       default="urls.txt", 
                       help="ملف الروابط (سطر لكل رابط)")
    
    # إضافة خيار --output-dir
    parser.add_argument("--output-dir", 
                       default="archive", 
                       help="مجلد الأرشيف")
    
    # إضافة خيار --max-concurrent
    # type=int: تحويل القيمة لعدد صحيح تلقائياً
    parser.add_argument("--max-concurrent", 
                       type=int, 
                       default=2, 
                       help="أقصى عدد تحميلات متوازية")
    
    # إضافة خيار --format
    parser.add_argument("--format", 
                       default="bestvideo+bestaudio/best", 
                       help="صيغة التحميل (format)")
    
    # ==== 2. معالجة الخيارات المدخلة ====
    args = parser.parse_args()
    # الآن يمكننا الوصول إلى:
    # args.urls_file
    # args.output_dir
    # args.max_concurrent
    # args.format
    
    # ==== 3. تحويل المسارات إلى Path objects ====
    urls_path = Path(args.urls_file)
    output_dir = Path(args.output_dir)
    
    # إنشاء مجلد الأرشيف إذا لم يكن موجوداً
    # parents=True: إنشاء المجلدات الأب أيضاً
    # exist_ok=True: لا خطأ إذا كان المجلد موجوداً مسبقاً
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # ==== 4. تحديد مسار ملف السجل ====
    log_file = output_dir / "archive.log"
    
    # ==== 5. قراءة الروابط من الملف ====
    try:
        urls = load_urls(urls_path)
    except FileNotFoundError as e:
        # إذا لم يوجد الملف، نطبع الخطأ ونخرج
        log(str(e))
        sys.exit(1)
    
    # ==== 6. التحقق من وجود روابط ====
    if not urls:
        log("لا يوجد أي روابط في ملف الروابط.", log_file=log_file)
        return  # الخروج من الدالة
    
    # ==== 7. تسجيل بداية العملية ====
    log(f"تم تحميل {len(urls)} رابط(اً) من {urls_path}", log_file=log_file)
    
    # ==== 8. تحديد عدد العمليات المتوازية ====
    # على الأقل 1، وكحد أقصى ما حدده المستخدم
    max_workers = max(1, int(args.max_concurrent))
    
    # ==== 9. بدء التحميل المتوازي ====
    # ThreadPoolExecutor: ينشئ مجموعة من الـ threads للتحميل المتوازي
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        
        # قائمة لحفظ الـ Future objects
        futures = []
        
        # لكل رابط، ننشئ مهمة تحميل
        for i, url in enumerate(urls, start=1):
            # enumerate(urls, start=1): يعطينا (1, url_1), (2, url_2), ...
            
            # submit(): إرسال مهمة للـ executor
            # سيتم تنفيذها عندما يتوفر thread
            future = executor.submit(download_one, i, url, output_dir, args.format, log_file)
            futures.append(future)
        
        # الانتظار حتى تنتهي جميع المهام
        for future in concurrent.futures.as_completed(futures):
            # as_completed(): يعطينا المهام بمجرد انتهائها (بأي ترتيب)
            # result(): الحصول على نتيجة المهمة (أو رفع استثناء إذا حدث خطأ)
            _ = future.result()  # نتجاهل النتيجة لأن download_one لا ترجع شيئاً
    
    # ==== 10. تسجيل انتهاء العملية ====
    log("انتهت عملية الأرشفة.", log_file=log_file)


# ==== 11. نقطة الدخول للبرنامج ====
if __name__ == "__main__":
    # هذا الشرط يتحقق فقط عند تشغيل الملف مباشرة
    # (وليس عند استيراده كمكتبة)
    main()
```

---

## ميزات الأداة

### ✅ الميزات المدمجة في الكود

1. **التحميل المتوازي**
   - يمكن تحميل عدة فيديوهات في نفس الوقت
   - يوفر الكثير من الوقت عند أرشفة مئات الفيديوهات
   - قابل للتحكم عبر `--max-concurrent`

2. **استكمال التحميل (Resume)**
   - إذا انقطع الإنترنت، يمكنك تشغيل السكربت مرة أخرى
   - سيستكمل من حيث توقف
   - يتخطى الفيديوهات المحملة تلقائياً

3. **معالجة الأخطاء**
   - لا يتوقف البرنامج بسبب فيديو واحد فاشل
   - يسجل كل الأخطاء في ملف السجل
   - يستمر حتى النهاية

4. **تنظيم تلقائي**
   - كل قناة في مجلد منفصل
   - أسماء الملفات تحتوي على التاريخ والعنوان
   - سهولة الوصول والبحث

5. **السجلات الشاملة**
   - ملف `archive.log` يحفظ كل شيء
   - وقت وتاريخ كل عملية
   - سهولة تتبع التقدم

### 🆕 الميزات الجديدة في الواجهة

1. **تنظيف الروابط من `?si=`**
   - يحذف معاملات التتبع تلقائياً
   - يحافظ على خصوصيتك
   - يزيل التكرار

2. **إضافة روابط متعددة**
   - واجهة نصية بسيطة
   - إحصائيات فورية (عدد الفيديوهات، القوائم، القنوات)
   - حفظ مباشر لملف `urls.txt`

3. **معاينة الكود المخصص**
   - توليد الكود حسب إعداداتك
   - نسخ بضغطة زر واحدة
   - جاهز للاستخدام مباشرة

---

## أمثلة الاستخدام

### مثال 1: أرشفة قائمة تشغيل كاملة

```bash
# إنشاء ملف urls.txt
echo "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf" > urls.txt

# تشغيل الأداة
python youtube_archiver.py --output-dir ./my_archive
```

### مثال 2: أرشفة عدة قوائم مع تحميل متوازي

```bash
# ملف urls.txt:
# https://youtube.com/playlist?list=PLAYLIST_1
# https://youtube.com/playlist?list=PLAYLIST_2
# https://youtube.com/playlist?list=PLAYLIST_3

python youtube_archiver.py \
  --urls-file urls.txt \
  --output-dir ./archive \
  --max-concurrent 3 \
  --format "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
```

### مثال 3: أرشفة قناة كاملة

```bash
# ملف urls.txt:
# https://www.youtube.com/@channel_name/videos

python youtube_archiver.py \
  --output-dir D:/YouTube_Archive \
  --max-concurrent 4
```

### مثال 4: تحميل بجودة محددة

```bash
# جودة 720p كحد أقصى (لتوفير المساحة)
python youtube_archiver.py --format "bestvideo[height<=720]+bestaudio"

# صوت فقط (MP3)
python youtube_archiver.py --format "bestaudio/best"
```

---

## نصائح وحلول للمشاكل

### 💡 نصائح للأرشفة الضخمة (1000+ فيديو)

1. **استخدم قرص صلب خارجي**
   ```bash
   python youtube_archiver.py --output-dir /media/external_hdd/archive
   ```

2. **لا تبالغ في التحميل المتوازي**
   - للإنترنت السريع: `--max-concurrent 4`
   - للإنترنت العادي: `--max-concurrent 2`
   - للإنترنت البطيء: `--max-concurrent 1`

3. **استخدم `screen` أو `tmux` في Linux**
   ```bash
   screen -S youtube_archiver
   python youtube_archiver.py
   # Ctrl+A ثم D للخروج وترك العملية تعمل
   ```

4. **تحديث yt-dlp بانتظام**
   ```bash
   pip install -U yt-dlp
   ```

### 🔧 حل المشاكل الشائعة

#### مشكلة: "HTTP Error 429: Too Many Requests"
**الحل:**
```bash
# قلل عدد التحميلات المتوازية
python youtube_archiver.py --max-concurrent 1

# أو أضف تأخير بين الطلبات (عدّل الكود):
'sleep_interval': 3,  # في ydl_opts
```

#### مشكلة: "Video unavailable"
**الحل:**
- تأكد أن الفيديو ليس خاصاً أو محذوفاً
- استخدم cookies للفيديوهات المحمية:
  ```bash
  # صدّر cookies من المتصفح
  # أضف في ydl_opts:
  'cookiefile': 'cookies.txt',
  ```

#### مشكلة: مساحة القرص ممتلئة
**الحل:**
```bash
# احذف ملفات .part (التحميلات غير المكتملة)
find ./archive -name "*.part" -delete

# أو حدد حجم أقصى للفيديو:
# في ydl_opts:
'max_filesize': 500 * 1024 * 1024,  # 500 MB
```

#### مشكلة: الفيديوهات بطيئة جداً
**الحل:**
```bash
# استخدم aria2c للتحميل (أسرع):
'external_downloader': 'aria2c',
'external_downloader_args': ['-x', '16', '-s', '16', '-k', '1M'],
```

### 📊 مراقبة التقدم

```bash
# عرض آخر 20 سطر من السجل
tail -n 20 archive/archive.log

# متابعة السجل مباشرة
tail -f archive/archive.log

# عد الفيديوهات المحملة
find archive -name "*.mp4" | wc -l
```

---

## الخلاصة

هذه الأداة صُممت خصيصاً للأرشفة الضخمة، مع:
- ✅ موثوقية عالية (استكمال، معالجة أخطاء)
- ✅ سرعة (تحميل متوازي)
- ✅ تنظيم تلقائي (مجلدات، أسماء واضحة)
- ✅ سجلات شاملة (تتبع كل شيء)
- ✅ خصوصية (تنظيف الروابط من التتبع)

**مناسبة لـ:**
- أرشفة قنوات كاملة
- حفظ قوائم تشغيل ضخمة
- نسخ احتياطي لمحتوى تعليمي
- أبحاث أكاديمية

استمتع بالأرشفة! 🎉
