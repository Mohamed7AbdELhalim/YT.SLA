# 📁 بنية الكود وشرح تفصيلي لكل سطر

هذا الملف يشرح بالتفصيل كل جزء من كود المشروع، التقنيات المستخدمة، وماذا يفعل كل سطر.

---

## 📋 فهرس المحتويات

1. [التقنيات المستخدمة](#التقنيات-المستخدمة)
2. [بنية ملف HTML](#بنية-ملف-html)
3. [شرح CSS والتنسيقات](#شرح-css-والتنسيقات)
4. [شرح JavaScript بالتفصيل](#شرح-javascript-بالتفصيل)
5. [شرح دوال تنظيف الروابط](#شرح-دوال-تنظيف-الروابط)
6. [شرح نظام الوسوم والمجلدات](#شرح-نظام-الوسوم-والمجلدات)
7. [شرح نظام التواريخ](#شرح-نظام-التواريخ)
8. [شرح نظام التخزين](#شرح-نظام-التخزين)
9. [شرح جلب العناوين](#شرح-جلب-العناوين)
10. [شرح مولّد كود بايثون](#شرح-مولد-كود-بايثون)

---

## التقنيات المستخدمة

### HTML5
```html
<!DOCTYPE html>
<!-- تعريف نوع المستند كـ HTML5 -->

<html lang="ar" dir="rtl">
<!-- lang="ar": تحديد اللغة العربية للصفحة -->
<!-- dir="rtl": اتجاه النص من اليمين لليسار -->
```

### Tailwind CSS (عبر CDN)
```html
<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
<!-- 
  تحميل Tailwind CSS من شبكة توصيل المحتوى (CDN)
  يوفر:
  - نظام ألوان جاهز (slate, emerald, blue, إلخ)
  - نظام تباعد (p-4, m-2, gap-3, إلخ)
  - نظام flexbox و grid
  - تصميم متجاوب (responsive)
-->
```

### JavaScript (Vanilla JS)
- لا نستخدم أي مكتبة JavaScript خارجية
- كل الكود مكتوب بـ JavaScript الأصلي
- يعمل على جميع المتصفحات الحديثة

---

## بنية ملف HTML

### 1. رأس الصفحة (Head)
```html
<head>
  <meta charset="UTF-8" />
  <!-- ترميز الأحرف UTF-8 لدعم العربية والرموز الخاصة -->
  
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <!-- 
    viewport: للتصميم المتجاوب
    width=device-width: عرض الصفحة = عرض الجهاز
    initial-scale=1.0: مستوى التكبير الابتدائي = 100%
  -->
  
  <title>أداة بايثون لأرشفة فيديوهات يوتيوب</title>
  <!-- عنوان الصفحة في شريط المتصفح -->
</head>
```

### 2. التنسيقات المخصصة
```html
<style>
  body { 
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; 
  }
  /* 
    استخدام خط النظام الافتراضي:
    - system-ui: خط النظام العام
    - -apple-system: لأجهزة Apple
    - BlinkMacSystemFont: لـ macOS
    - "Segoe UI": لـ Windows
    - sans-serif: بديل أخير
  */
  
  textarea { direction: ltr; }
  code { direction: ltr; }
  /* 
    الروابط والأكواد تُكتب من اليسار لليمين
    حتى لو كانت الصفحة RTL
  */
</style>
```

### 3. بنية الصفحة الرئيسية
```html
<body class="bg-slate-950 text-slate-100 min-h-screen">
  <!-- 
    bg-slate-950: خلفية داكنة جداً
    text-slate-100: نص فاتح
    min-h-screen: الحد الأدنى للارتفاع = ارتفاع الشاشة
  -->
  
  <div class="max-w-6xl mx-auto px-4 py-8">
    <!-- 
      max-w-6xl: عرض أقصى 1152px
      mx-auto: توسيط أفقي
      px-4: padding أفقي 16px
      py-8: padding رأسي 32px
    -->
```

---

## شرح JavaScript بالتفصيل

### 1. المتغيرات العامة

```javascript
let urlEntries = [];
// مصفوفة تحتوي على كل الروابط مع بياناتها
// كل عنصر يحتوي على:
// {
//   url: "...",        // الرابط المنظف
//   tag: "#shorts",    // الوسم الرئيسي
//   folder: "shorts",  // المجلد
//   siteTag: "#youtube", // وسم الموقع
//   extraTags: "",     // أوسمة إضافية
//   type: "short",     // نوع الرابط
//   dateValue: "",     // قيمة التاريخ (ISO format)
//   dayLabel: "",      // تسمية اليوم
//   weekLabel: "",     // تسمية الأسبوع
//   title: ""          // عنوان الفيديو
// }

const STORAGE_KEY = 'youtube_archiver_links_v1';
// مفتاح التخزين المحلي في المتصفح
// نستخدم رقم إصدار (v1) للتوافق المستقبلي
```

### 2. معاملات التتبع المحذوفة

```javascript
const trackingParams = [
  'si',        // معامل مشاركة يوتيوب الجديد
  'feature',   // مصدر الوصول للفيديو
  'fbclid',    // معرّف فيسبوك
  'gclid',     // معرّف جوجل
  'kw',        // كلمة مفتاحية
  'spm',       // تتبع علي بابا
  'utm_source',    // UTM parameters
  'utm_medium',
  'utm_campaign'
];
// هذه المعاملات تُستخدم للتتبع ولا تؤثر على الفيديو
// نحذفها للحفاظ على الخصوصية

const importantParams = ['v', 'list', 't', 'index'];
// v: معرّف الفيديو (ضروري)
// list: معرّف قائمة التشغيل
// t: وقت البداية (مثل t=120 للبدء من الدقيقة 2)
// index: ترتيب الفيديو في القائمة
```

---

## شرح دوال تنظيف الروابط

### دالة cleanYouTubeUrl

```javascript
function cleanYouTubeUrl(url) {
  try {
    const trimmed = url.trim();
    // إزالة المسافات من البداية والنهاية
    
    if (!trimmed) return '';
    // إذا كان فارغاً، نرجع نص فارغ
    
    let urlObj = new URL(trimmed);
    // تحويل النص إلى كائن URL للتعامل معه بسهولة
    // مثال: URL("https://youtube.com/watch?v=abc&si=123")
    // urlObj.hostname = "youtube.com"
    // urlObj.pathname = "/watch"
    // urlObj.searchParams = {v: "abc", si: "123"}
    
    const originalSearch = new URLSearchParams(urlObj.search);
    // حفظ المعاملات الأصلية قبل التعديل
    
    const hostname = urlObj.hostname.toLowerCase();
    // الحصول على اسم الموقع بأحرف صغيرة

    // تحويل youtu.be إلى youtube.com
    if (hostname === 'youtu.be' || hostname === 'www.youtu.be') {
      const videoId = urlObj.pathname.replace('/', '');
      // استخراج معرّف الفيديو من المسار
      // youtu.be/abc123 → abc123
      
      if (videoId) {
        const newUrl = new URL('https://youtube.com/watch');
        newUrl.searchParams.set('v', videoId);
        // إنشاء رابط جديد بصيغة youtube.com
        
        // نقل المعاملات المهمة
        ['t', 'list', 'index'].forEach(param => {
          if (originalSearch.has(param)) {
            newUrl.searchParams.set(param, originalSearch.get(param));
          }
        });
        
        urlObj = newUrl;
      }
    }

    // حذف معاملات التتبع
    trackingParams.forEach(param => urlObj.searchParams.delete(param));
    
    // الإبقاء على المعاملات المهمة فقط
    const filteredParams = new URLSearchParams();
    importantParams.forEach(param => {
      if (urlObj.searchParams.has(param)) {
        filteredParams.set(param, urlObj.searchParams.get(param));
      }
    });
    urlObj.search = filteredParams.toString();
    
    // إرجاع الرابط النظيف بدون / في النهاية
    return urlObj.toString().replace(/\/$/, '');
    
  } catch (e) {
    // إذا حدث خطأ (رابط غير صالح)، نرجع الرابط كما هو
    return url.trim();
  }
}
```

### دالة classifyUrlType

```javascript
function classifyUrlType(url) {
  const lower = url.toLowerCase();
  // تحويل لأحرف صغيرة للمقارنة
  
  if (lower.includes('/shorts/')) return 'short';
  // إذا يحتوي على /shorts/ = شورت
  
  if (lower.includes('playlist?') || lower.includes('list=')) return 'playlist';
  // إذا يحتوي على playlist? أو list= = قائمة تشغيل
  
  if (lower.includes('/@') || lower.includes('/channel/') || lower.includes('/c/')) return 'channel';
  // إذا يحتوي على /@ أو /channel/ أو /c/ = قناة
  
  if (lower.includes('watch?v=') || lower.includes('youtu.be/')) return 'video';
  // إذا يحتوي على watch?v= = فيديو
  
  return 'other';
  // أي شيء آخر
}
```

---

## شرح نظام الوسوم والمجلدات

### دالة getSiteTag

```javascript
function getSiteTag(hostname) {
  const cleanHost = hostname.replace(/^www\./i, '').toLowerCase();
  // إزالة www. من البداية وتحويل لأحرف صغيرة
  // www.youtube.com → youtube.com
  
  if (cleanHost.endsWith('youtube.com') || cleanHost.endsWith('youtu.be')) {
    return '#youtube';
  }
  // إذا كان يوتيوب، نرجع #youtube
  
  const base = cleanHost.split('.')[0] || 'site';
  return `#${base}`;
  // لأي موقع آخر، نأخذ الجزء الأول
  // vimeo.com → #vimeo
  // dailymotion.com → #dailymotion
}
```

### دالة shouldUseYouTubeSegment

```javascript
function shouldUseYouTubeSegment(segment) {
  if (!segment) return false;
  
  const normalized = segment.toLowerCase();
  
  if (normalized.startsWith('@')) return true;
  // أسماء القنوات الجديدة تبدأ بـ @
  
  const allowed = [
    'shorts',    // فيديوهات قصيرة
    'playlist',  // قوائم التشغيل
    'channel',   // القنوات (الصيغة القديمة)
    'user',      // المستخدمين (صيغة قديمة)
    'c',         // القنوات المخصصة
    'live',      // البث المباشر
    'feed',      // الخلاصات
    'results',   // نتائج البحث
    'gaming'     // قسم الألعاب
  ];
  
  return allowed.includes(normalized);
  // نرجع true فقط إذا كان المسار معروفاً
  // هذا يمنع استخدام معرّف الفيديو كوسم
  // مثال: youtube.com/_gYIWm_v19U
  // _gYIWm_v19U ليس مسار معروف، فلا يُستخدم كوسم
}
```

### دالة extractTagAndFolder

```javascript
function extractTagAndFolder(url) {
  try {
    const urlObj = new URL(url);
    const hostname = urlObj.hostname.toLowerCase();
    const siteTag = getSiteTag(urlObj.hostname);
    // استخراج وسم الموقع
    
    const segments = urlObj.pathname
      .split('/')           // تقسيم المسار
      .filter(Boolean)      // إزالة العناصر الفارغة
      .map(seg => decodeURIComponent(seg));  // فك ترميز URL
    // مثال: "/shorts/abc123" → ["shorts", "abc123"]
    
    let folderSegment = segments[0] || 'videos';
    // الجزء الأول من المسار = المجلد
    
    if (hostname.includes('youtube.com')) {
      const firstSegment = (segments[0] || '').toLowerCase();
      if (!shouldUseYouTubeSegment(firstSegment)) {
        folderSegment = 'videos';
        // إذا لم يكن مسار يوتيوب معروف، نستخدم "videos"
      }
    }
    
    // توليد الوسم من المجلد
    const normalizedTag = folderSegment === 'videos' 
      ? '#videos' 
      : normalizeTagValue(folderSegment);
    
    return { 
      primaryTag: normalizedTag || '#videos', 
      folder: folderSegment || 'videos', 
      siteTag 
    };
    
  } catch (e) {
    return { primaryTag: '#videos', folder: 'videos', siteTag: '#site' };
  }
}
```

---

## شرح نظام التواريخ

### أنماط التاريخ المدعومة

```javascript
const datePatterns = [
  { 
    regex: /(\d{4})[\/.\-](\d{1,2})[\/.\-](\d{1,2})/, 
    order: ['year', 'month', 'day'] 
  },
  // 2024/01/15 أو 2024-01-15 أو 2024.01.15
  
  { 
    regex: /(\d{1,2})[\/.\-](\d{1,2})[\/.\-](\d{4})/, 
    order: ['day', 'month', 'year'] 
  },
  // 15/01/2024 أو 15-01-2024
  
  { 
    regex: /(\d{4})(\d{2})(\d{2})/, 
    order: ['year', 'month', 'day'] 
  },
  // 20240115 (بدون فواصل)
];
```

### دالة getISOWeek

```javascript
function getISOWeek(date) {
  // حساب رقم الأسبوع حسب معيار ISO 8601
  
  const workingDate = new Date(
    Date.UTC(date.getFullYear(), date.getMonth(), date.getDate())
  );
  // إنشاء تاريخ UTC لتجنب مشاكل المنطقة الزمنية
  
  const dayNum = workingDate.getUTCDay() || 7;
  // الحصول على رقم اليوم (1-7)
  // الأحد = 0 يصبح 7
  
  workingDate.setUTCDate(workingDate.getUTCDate() + 4 - dayNum);
  // الانتقال ليوم الخميس من نفس الأسبوع
  // (الأسبوع ISO يُحدد بالخميس الذي يقع فيه)
  
  const yearStart = new Date(Date.UTC(workingDate.getUTCFullYear(), 0, 1));
  // أول يوم في السنة
  
  const diff = (workingDate - yearStart) / 86400000 + 1;
  // الفرق بالأيام (86400000 = مللي ثانية في يوم)
  
  return Math.ceil(diff / 7);
  // قسمة على 7 وتقريب لأعلى = رقم الأسبوع
}
```

---

## شرح نظام التخزين

### حفظ في LocalStorage

```javascript
function persistEntriesToLocalStorage() {
  try {
    const payload = {
      generatedAt: new Date().toISOString(),
      // وقت الحفظ
      
      total: urlEntries.length,
      // عدد الروابط
      
      entries: urlEntries,
      // البيانات الكاملة
    };
    
    localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
    // تحويل الكائن لنص JSON وحفظه
    
  } catch (e) {
    console.warn('تعذر حفظ البيانات في المتصفح:', e);
    // قد يفشل إذا امتلأت المساحة المتاحة
  }
}
```

### تحميل من LocalStorage

```javascript
function loadEntriesFromLocalStorage() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    // قراءة النص المخزن
    
    if (!raw) return;
    // إذا لم يوجد شيء، نخرج
    
    const parsed = JSON.parse(raw);
    // تحويل النص JSON لكائن JavaScript
    
    const entriesArray = Array.isArray(parsed) ? parsed : parsed.entries;
    // دعم الصيغة القديمة (مصفوفة مباشرة) والجديدة (كائن مع entries)
    
    if (!Array.isArray(entriesArray) || !entriesArray.length) return;
    
    // إعادة بناء البيانات مع التحقق من كل حقل
    urlEntries = entriesArray.map((item) => ({
      url: item.url,
      tag: item.tag,
      folder: item.folder,
      siteTag: item.siteTag,
      extraTags: item.extraTags || '',
      type: item.type || classifyUrlType(item.url || ''),
      dateValue: item.dateValue || '',
      dayLabel: item.dayLabel || 'بدون تاريخ',
      weekLabel: item.weekLabel || 'بدون تاريخ',
      title: item.title || '',
    }));
    
    // تحديث الواجهة
    document.getElementById('urlsInput').value = urlEntries.map(e => e.url).join('\n');
    updateUrlsStats(urlEntries);
    renderEntriesTable();
    
  } catch (e) {
    console.warn('تعذر تحميل البيانات المخزنة:', e);
  }
}
```

### تصدير JSON

```javascript
document.getElementById('exportDataBtn').addEventListener('click', function(e) {
  e.preventDefault();
  e.stopPropagation();
  // منع أي سلوك افتراضي
  
  if (!urlEntries.length) {
    alert('لا توجد بيانات لتصديرها!');
    return;
  }

  try {
    const payload = {
      generatedAt: new Date().toISOString(),
      total: urlEntries.length,
      entries: urlEntries.map(entry => ({
        url: entry.url,
        tag: entry.tag,
        folder: entry.folder,
        siteTag: entry.siteTag,
        extraTags: entry.extraTags,
        type: entry.type,
        dateValue: entry.dateValue,
        dayLabel: entry.dayLabel,
        weekLabel: entry.weekLabel,
        title: entry.title || '',
      })),
    };

    const jsonString = JSON.stringify(payload, null, 2);
    // null, 2 = تنسيق مقروء مع مسافتين
    
    const blob = new Blob([jsonString], { type: 'application/json;charset=utf-8' });
    // إنشاء كائن Blob (ملف في الذاكرة)
    
    const filename = 'youtube_links_with_tags.json';
    
    // دعم المتصفحات القديمة
    if (window.navigator && window.navigator.msSaveOrOpenBlob) {
      window.navigator.msSaveOrOpenBlob(blob, filename);
      return;
    }
    
    // إنشاء رابط تنزيل
    const downloadUrl = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename;
    link.style.display = 'none';
    
    document.body.appendChild(link);
    link.click();
    // محاكاة النقر لبدء التنزيل
    
    setTimeout(function() {
      document.body.removeChild(link);
      URL.revokeObjectURL(downloadUrl);
      // تنظيف الذاكرة بعد التنزيل
    }, 100);
    
  } catch (error) {
    console.error('خطأ أثناء التصدير:', error);
    alert('حدث خطأ: ' + error.message);
  }
});
```

---

## شرح جلب العناوين

```javascript
async function fetchYouTubeTitles() {
  if (!urlEntries.length) {
    alert('لا توجد روابط لجلب عناوينها.');
    return;
  }

  flashMessage('جاري جلب عناوين الفيديوهات...', 'text-blue-300');

  let updated = 0;  // عدد الروابط المحدثة
  let skipped = 0;  // عدد الروابط المتخطاة
  let failed = 0;   // عدد الفشل

  for (const entry of urlEntries) {
    // نهتم فقط بفيديوهات يوتيوب
    if (entry.siteTag !== '#youtube' || 
        (entry.type !== 'video' && entry.type !== 'short')) {
      skipped++;
      continue;
    }
    
    // تخطي إذا العنوان موجود
    if (entry.title && entry.title.trim()) {
      skipped++;
      continue;
    }

    try {
      // استخدام YouTube oEmbed API
      const oembedUrl = 'https://www.youtube.com/oembed?url=' + 
                        encodeURIComponent(entry.url) + 
                        '&format=json';
      
      const res = await fetch(oembedUrl);
      // طلب HTTP غير متزامن
      
      if (!res.ok) {
        failed++;
        continue;
      }
      
      const data = await res.json();
      // تحويل الاستجابة لـ JSON
      
      if (data && typeof data.title === 'string') {
        entry.title = data.title;
        updated++;
      } else {
        failed++;
      }
      
    } catch (e) {
      console.warn('تعذر جلب عنوان الفيديو:', e);
      failed++;
    }
  }

  // حفظ التغييرات
  persistEntriesToLocalStorage();
  renderEntriesTable();
  
  // عرض النتيجة
  flashMessage(`تم تحديث ${updated} رابطاً، تخطّي ${skipped}، فشل ${failed}.`);
}
```

---

## شرح مولّد كود بايثون

```javascript
function buildPythonCode(config) {
  const { urlsFile, outputDir, maxConcurrent, format, writeMetadata } = config;
  // استخراج الإعدادات من الكائن
  
  // بناء أعلام الميتاداتا إذا مفعّلة
  const metadataFlags = writeMetadata
    ? `        'writeinfojson': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'writethumbnail': True,`
    : "";

  // Template literal (قالب نصي متعدد الأسطر)
  const code = `#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
أداة أرشفة فيديوهات يوتيوب
...
"""

import argparse
...

def main():
    parser.add_argument("--urls-file", default="${urlsFile}", ...)
    parser.add_argument("--output-dir", default="${outputDir}", ...)
    parser.add_argument("--max-concurrent", default=${maxConcurrent}, ...)
    parser.add_argument("--format", default="${format}", ...)
    ...

${metadataFlags}
    ...
`;

  return code;
}
```

---

## ملخص التقنيات المستخدمة

| التقنية | الاستخدام |
|---------|----------|
| HTML5 | بنية الصفحة |
| Tailwind CSS | التنسيقات والتصميم المتجاوب |
| JavaScript ES6+ | المنطق والتفاعل |
| LocalStorage API | التخزين المحلي |
| Fetch API | جلب عناوين الفيديوهات |
| URL API | تحليل وتعديل الروابط |
| Blob API | إنشاء ملفات للتنزيل |
| FileReader API | قراءة ملفات JSON |
| Template Literals | توليد كود بايثون |
| Intl.DateTimeFormat | تنسيق التواريخ بالعربية |

---

## نصائح للمطورين

1. **للتعديل على الكود:**
   - ابحث عن الدالة المطلوبة بالاسم
   - اقرأ التعليقات المرفقة
   - اختبر التغييرات في المتصفح

2. **لإضافة ميزة جديدة:**
   - أضف الدالة الجديدة
   - اربطها بالواجهة (addEventListener)
   - أضف التحديث للتخزين إن لزم

3. **لتصحيح الأخطاء:**
   - استخدم console.log
   - افتح Developer Tools (F12)
   - راجع tab الـ Console

---

*آخر تحديث: 2024*
