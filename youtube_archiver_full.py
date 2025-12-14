#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    أداة أرشفة فيديوهات يوتيوب المتقدمة                        ║
║                   YouTube Video Archiver - Full Version                      ║
║                              الإصدار 2.0.0                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

الميزات:
─────────
• تنظيف الروابط من معاملات التتبع (?si=, &feature=, &fbclid=, إلخ)
• تحويل روابط youtu.be إلى youtube.com تلقائياً
• استخراج وسوم تلقائية (وسم الموقع + وسم المسار)
• تصنيف نوع الرابط (فيديو، شورت، قائمة تشغيل، قناة، صفحة ويب)
• استخراج التاريخ من الرابط وحساب رقم الأسبوع
• جلب عناوين الفيديوهات من يوتيوب
• جلب معلومات قوائم التشغيل (العنوان، عدد الفيديوهات، المشاهدات)
• جلب عناوين صفحات الويب العامة
• قراءة/كتابة ملف JSON مع كل البيانات
• تحميل الفيديوهات باستخدام yt-dlp
• سجل تفصيلي لكل العمليات

طريقة الاستخدام:
────────────────
    python youtube_archiver_full.py --help

أمثلة:
──────
    # تنظيف وتصنيف الروابط فقط
    python youtube_archiver_full.py --urls-file urls.txt --classify-only

    # جلب العناوين من الإنترنت
    python youtube_archiver_full.py --json-file links_data.json --fetch-titles

    # تحميل الفيديوهات
    python youtube_archiver_full.py --json-file links_data.json --download --output-dir ./archive

المؤلف: YouTube Archiver Team
الترخيص: MIT License
"""

# ══════════════════════════════════════════════════════════════════════════════
# استيراد المكتبات
# ══════════════════════════════════════════════════════════════════════════════

import argparse          # لمعالجة خيارات سطر الأوامر
import concurrent.futures # للتحميل المتوازي (عدة فيديوهات في نفس الوقت)
import datetime as dt    # للتعامل مع التواريخ والأوقات
import json              # لقراءة وكتابة ملفات JSON
import os                # للتعامل مع نظام الملفات
import re                # للتعبيرات النمطية (Regular Expressions)
import sys               # للتحكم في النظام والخروج من البرنامج
from pathlib import Path # للتعامل مع المسارات بطريقة حديثة
from typing import Any, Dict, List, Optional, Tuple  # لتحديد أنواع البيانات
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse  # لتحليل الروابط

# ══════════════════════════════════════════════════════════════════════════════
# محاولة استيراد المكتبات الاختيارية
# ══════════════════════════════════════════════════════════════════════════════

# مكتبة yt-dlp لتحميل الفيديوهات
try:
    from yt_dlp import YoutubeDL
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False
    print("[تحذير] مكتبة yt-dlp غير مثبتة. لن تعمل ميزة التحميل.")
    print("        للتثبيت: pip install yt-dlp")

# مكتبة requests لجلب البيانات من الإنترنت
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("[تحذير] مكتبة requests غير مثبتة. لن تعمل ميزة جلب العناوين.")
    print("        للتثبيت: pip install requests")

# مكتبة BeautifulSoup لتحليل صفحات HTML
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print("[تحذير] مكتبة beautifulsoup4 غير مثبتة. لن تعمل ميزة جلب عناوين صفحات الويب.")
    print("        للتثبيت: pip install beautifulsoup4")


# ══════════════════════════════════════════════════════════════════════════════
# الثوابت والإعدادات
# ══════════════════════════════════════════════════════════════════════════════

# معاملات التتبع التي سيتم حذفها من الروابط
TRACKING_PARAMS: List[str] = [
    'si',           # معامل مشاركة يوتيوب الجديد
    'feature',      # مصدر الوصول للفيديو
    'fbclid',       # معرّف فيسبوك للتتبع
    'gclid',        # معرّف جوجل للإعلانات
    'kw',           # كلمة مفتاحية
    'spm',          # تتبع علي بابا
    'utm_source',   # مصدر الحملة التسويقية
    'utm_medium',   # وسيط الحملة
    'utm_campaign', # اسم الحملة
    'utm_term',     # مصطلح البحث
    'utm_content',  # محتوى الإعلان
]

# المعاملات المهمة التي يجب الحفاظ عليها
IMPORTANT_PARAMS: List[str] = [
    'v',      # معرّف الفيديو (ضروري)
    'list',   # معرّف قائمة التشغيل
    't',      # وقت البداية في الفيديو
    'index',  # ترتيب الفيديو في القائمة
]

# المسارات المعروفة في يوتيوب التي تُعتبر وسوماً صالحة
YOUTUBE_VALID_SEGMENTS: List[str] = [
    'shorts',    # فيديوهات قصيرة
    'playlist',  # قوائم التشغيل
    'channel',   # القنوات (الصيغة القديمة)
    'user',      # المستخدمين (صيغة قديمة)
    'c',         # القنوات المخصصة
    'live',      # البث المباشر
    'feed',      # الخلاصات
    'results',   # نتائج البحث
    'gaming',    # قسم الألعاب
]

# المسارات الشائعة للمواقع الأخرى
COMMON_WEB_PATHS: List[str] = [
    'abs', 'pdf', 'article', 'articles', 'post', 'posts', 'blog', 'news',
    'docs', 'documentation', 'wiki', 'help', 'support', 'faq',
    'video', 'videos', 'watch', 'embed', 'channel', 'user', 'playlist',
    'search', 'results', 'explore', 'trending', 'popular',
    'category', 'categories', 'tag', 'tags', 'topic', 'topics',
    'page', 'pages', 'view', 'read', 'show', 'detail', 'details',
    'product', 'products', 'item', 'items', 'shop', 'store',
    'download', 'downloads', 'file', 'files', 'media',
    'gallery', 'image', 'images', 'photo', 'photos', 'picture', 'pictures',
    'music', 'audio', 'sound', 'podcast', 'episode',
    'course', 'courses', 'lesson', 'lessons', 'tutorial', 'tutorials',
    'paper', 'papers', 'research', 'publication', 'publications',
    'project', 'projects', 'repo', 'repository', 'code',
    'forum', 'thread', 'discussion', 'comment', 'comments',
    'profile', 'account', 'settings', 'dashboard',
    'api', 'v1', 'v2', 'v3',
]

# أنماط التاريخ للبحث في الروابط
DATE_PATTERNS: List[Tuple[str, List[str]]] = [
    # السنة-الشهر-اليوم (2024-01-15 أو 2024/01/15)
    (r'(\d{4})[\/.\-](\d{1,2})[\/.\-](\d{1,2})', ['year', 'month', 'day']),
    # اليوم-الشهر-السنة (15-01-2024 أو 15/01/2024)
    (r'(\d{1,2})[\/.\-](\d{1,2})[\/.\-](\d{4})', ['day', 'month', 'year']),
    # بدون فواصل (20240115)
    (r'(\d{4})(\d{2})(\d{2})', ['year', 'month', 'day']),
]


# ══════════════════════════════════════════════════════════════════════════════
# دوال السجلات والطباعة
# ══════════════════════════════════════════════════════════════════════════════

def log(message: str, level: str = "INFO", log_file: Optional[Path] = None) -> None:
    """
    طباعة رسالة على الشاشة وحفظها في ملف السجل
    
    المعاملات:
        message: النص المراد طباعته
        level: مستوى الرسالة (INFO, WARNING, ERROR, SUCCESS)
        log_file: مسار ملف السجل (اختياري)
    """
    # الحصول على التاريخ والوقت الحالي
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # تحديد رمز المستوى
    level_icons = {
        "INFO": "ℹ️",
        "WARNING": "⚠️",
        "ERROR": "❌",
        "SUCCESS": "✅",
    }
    icon = level_icons.get(level, "•")
    
    # تنسيق السطر
    line = f"[{now}] {icon} [{level}] {message}"
    
    # طباعة على الشاشة
    print(line)
    
    # حفظ في ملف السجل إذا تم تحديده
    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with log_file.open("a", encoding="utf-8") as f:
            f.write(line + "\n")


def print_header(title: str) -> None:
    """طباعة عنوان قسم بتنسيق جميل"""
    width = 70
    print("\n" + "═" * width)
    print(f"  {title}")
    print("═" * width)


def print_stats(entries: List[Dict]) -> None:
    """طباعة إحصائيات الروابط"""
    if not entries:
        print("لا توجد روابط.")
        return
    
    # حساب الإحصائيات
    total = len(entries)
    types_count = {}
    sites_count = {}
    tags_count = {}
    
    for entry in entries:
        # أنواع الروابط
        url_type = entry.get('type', 'other')
        types_count[url_type] = types_count.get(url_type, 0) + 1
        
        # المواقع
        site_tag = entry.get('siteTag', '#unknown')
        sites_count[site_tag] = sites_count.get(site_tag, 0) + 1
        
        # الوسوم
        tag = entry.get('tag', '')
        if tag:
            tags_count[tag] = tags_count.get(tag, 0) + 1
    
    print(f"\n📊 إحصائيات الروابط:")
    print(f"   • الإجمالي: {total}")
    print(f"   • الأنواع: {types_count}")
    print(f"   • المواقع: {sites_count}")
    print(f"   • أشهر الوسوم: {dict(sorted(tags_count.items(), key=lambda x: x[1], reverse=True)[:5])}")


# ══════════════════════════════════════════════════════════════════════════════
# دوال تنظيف الروابط
# ══════════════════════════════════════════════════════════════════════════════

def clean_url(url: str) -> str:
    """
    تنظيف الرابط من معاملات التتبع مع الحفاظ على المعاملات المهمة
    
    المعاملات:
        url: الرابط الأصلي
    
    العودة:
        الرابط بعد التنظيف
    
    مثال:
        >>> clean_url("https://youtube.com/watch?v=abc123&si=xyz&feature=share")
        'https://youtube.com/watch?v=abc123'
    """
    try:
        url = url.strip()
        if not url:
            return ''
        
        # تحليل الرابط إلى أجزائه
        parsed = urlparse(url)
        hostname = parsed.hostname.lower() if parsed.hostname else ''
        
        # تحويل youtu.be إلى youtube.com
        if hostname in ('youtu.be', 'www.youtu.be'):
            # استخراج معرّف الفيديو من المسار
            video_id = parsed.path.lstrip('/')
            if video_id:
                # بناء رابط youtube.com الجديد
                new_query = {'v': video_id}
                
                # نقل المعاملات المهمة
                old_params = parse_qs(parsed.query)
                for param in ['t', 'list', 'index']:
                    if param in old_params:
                        new_query[param] = old_params[param][0]
                
                return f"https://youtube.com/watch?{urlencode(new_query)}"
        
        # تصفية المعاملات
        query_params = parse_qs(parsed.query)
        filtered_params = {}
        
        for param, values in query_params.items():
            # حذف معاملات التتبع
            if param.lower() in TRACKING_PARAMS:
                continue
            # الحفاظ على المعاملات المهمة فقط لروابط يوتيوب
            if 'youtube.com' in hostname or 'youtu.be' in hostname:
                if param.lower() in IMPORTANT_PARAMS:
                    filtered_params[param] = values[0]
            else:
                # للمواقع الأخرى، نحتفظ بكل المعاملات غير التتبعية
                filtered_params[param] = values[0]
        
        # إعادة بناء الرابط
        new_query = urlencode(filtered_params) if filtered_params else ''
        cleaned = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path.rstrip('/'),
            parsed.params,
            new_query,
            ''  # إزالة الـ fragment
        ))
        
        return cleaned
        
    except Exception as e:
        log(f"خطأ في تنظيف الرابط: {url} - {e}", "WARNING")
        return url.strip()


# ══════════════════════════════════════════════════════════════════════════════
# دوال تصنيف الروابط
# ══════════════════════════════════════════════════════════════════════════════

def classify_url_type(url: str) -> str:
    """
    تحديد نوع الرابط (فيديو، شورت، قائمة تشغيل، قناة، صفحة ويب)
    
    المعاملات:
        url: الرابط المراد تصنيفه
    
    العودة:
        نوع الرابط كنص
    """
    url_lower = url.lower()
    
    try:
        parsed = urlparse(url)
        hostname = (parsed.hostname or '').lower().replace('www.', '')
        
        # تصنيف روابط يوتيوب
        if 'youtube.com' in hostname or 'youtu.be' in hostname:
            if '/shorts/' in url_lower:
                return 'short'
            if 'playlist?' in url_lower or 'list=' in url_lower:
                return 'playlist'
            if '/@' in url or '/channel/' in url_lower or '/c/' in url_lower:
                return 'channel'
            if 'watch?v=' in url_lower or 'youtu.be/' in url_lower:
                return 'video'
            return 'video'
        
        # المواقع الأخرى
        return 'webpage'
        
    except Exception:
        return 'other'


def get_site_tag(hostname: str) -> str:
    """
    استخراج وسم الموقع من اسم الدومين
    
    المعاملات:
        hostname: اسم الدومين (مثل www.youtube.com)
    
    العودة:
        وسم الموقع (مثل #youtube)
    """
    # تنظيف اسم الدومين
    clean_host = hostname.lower().replace('www.', '')
    
    # يوتيوب
    if 'youtube.com' in clean_host or 'youtu.be' in clean_host:
        return '#youtube'
    
    # استخراج الجزء الأول من الدومين
    base = clean_host.split('.')[0]
    return f'#{base}' if base else '#site'


def get_valid_path_segment(pathname: str) -> Optional[str]:
    """
    استخراج المسار الأول الصالح من رابط (للمواقع غير يوتيوب)
    
    المعاملات:
        pathname: مسار الرابط (مثل /abs/1809.00219)
    
    العودة:
        المسار الصالح أو None
    """
    # تقسيم المسار
    segments = [s for s in pathname.split('/') if s]
    if not segments:
        return None
    
    first_segment = segments[0]
    
    # تجاهل المعرّفات الرقمية
    if re.match(r'^[\d.]+$', first_segment):
        return None
    
    # تجاهل المعرّفات الطويلة العشوائية
    if re.match(r'^[a-zA-Z0-9_-]{10,}$', first_segment):
        if not re.search(r'[aeiou]', first_segment, re.IGNORECASE):
            return None
    
    # تجاهل المسارات القصيرة جداً
    if len(first_segment) < 2:
        return None
    
    # التحقق من المسارات الشائعة
    if first_segment.lower() in COMMON_WEB_PATHS:
        return first_segment
    
    # التحقق من أنه يبدو ككلمة عادية
    if re.match(r'^[a-zA-Z][a-zA-Z0-9_-]{1,20}$', first_segment):
        if re.search(r'[aeiou]', first_segment, re.IGNORECASE):
            return first_segment
    
    return None


def should_use_youtube_segment(segment: str) -> bool:
    """
    التحقق مما إذا كان المسار صالحاً كوسم ليوتيوب
    
    المعاملات:
        segment: جزء المسار (مثل shorts, playlist)
    
    العودة:
        True إذا كان صالحاً، False إذا لم يكن
    """
    if not segment:
        return False
    
    normalized = segment.lower()
    
    # أسماء القنوات الجديدة تبدأ بـ @
    if normalized.startswith('@'):
        return True
    
    return normalized in YOUTUBE_VALID_SEGMENTS


def extract_tag_and_folder(url: str) -> Dict[str, str]:
    """
    استخراج الوسم والمجلد ووسم الموقع من الرابط
    
    المعاملات:
        url: الرابط المراد تحليله
    
    العودة:
        قاموس يحتوي على: primaryTag, folder, siteTag
    """
    try:
        parsed = urlparse(url)
        hostname = (parsed.hostname or '').lower().replace('www.', '')
        site_tag = get_site_tag(parsed.hostname or '')
        
        # استخراج أجزاء المسار
        segments = [s for s in parsed.path.split('/') if s]
        
        folder_segment = 'general'
        primary_tag = '#general'
        
        # معالجة روابط يوتيوب
        if 'youtube.com' in hostname or 'youtu.be' in hostname:
            first_segment = segments[0].lower() if segments else ''
            if should_use_youtube_segment(first_segment):
                folder_segment = segments[0]
                primary_tag = f'#{folder_segment}'
            else:
                folder_segment = 'videos'
                primary_tag = '#videos'
        
        # معالجة المواقع الأخرى
        else:
            valid_segment = get_valid_path_segment(parsed.path)
            if valid_segment:
                folder_segment = valid_segment
                primary_tag = f'#{valid_segment}'
            else:
                # استخدام اسم الموقع كمجلد
                site_name = hostname.split('.')[0]
                folder_segment = site_name or 'general'
                primary_tag = f'#{folder_segment}'
        
        return {
            'primaryTag': primary_tag or '#general',
            'folder': folder_segment or 'general',
            'siteTag': site_tag,
        }
        
    except Exception as e:
        log(f"خطأ في استخراج الوسم: {url} - {e}", "WARNING")
        return {
            'primaryTag': '#general',
            'folder': 'general',
            'siteTag': '#site',
        }


# ══════════════════════════════════════════════════════════════════════════════
# دوال التواريخ
# ══════════════════════════════════════════════════════════════════════════════

def detect_date_from_url(url: str) -> Optional[dt.date]:
    """
    محاولة استخراج التاريخ من الرابط
    
    المعاملات:
        url: الرابط المراد البحث فيه
    
    العودة:
        كائن date إذا وُجد تاريخ، None إذا لم يوجد
    """
    try:
        parsed = urlparse(url)
        # البحث في المسار والمعاملات
        search_text = f"{parsed.path} {parsed.query}"
        
        for pattern, order in DATE_PATTERNS:
            match = re.search(pattern, search_text)
            if match:
                # استخراج القيم
                values = {}
                for i, key in enumerate(order):
                    values[key] = int(match.group(i + 1))
                
                year = values.get('year', 0)
                month = values.get('month', 0)
                day = values.get('day', 0)
                
                # التحقق من صحة القيم
                if 1 <= month <= 12 and 1 <= day <= 31 and 1900 <= year <= 2100:
                    try:
                        return dt.date(year, month, day)
                    except ValueError:
                        continue
        
        return None
        
    except Exception:
        return None


def get_iso_week(date: dt.date) -> int:
    """
    حساب رقم الأسبوع حسب معيار ISO 8601
    
    المعاملات:
        date: كائن التاريخ
    
    العودة:
        رقم الأسبوع (1-53)
    """
    return date.isocalendar()[1]


def format_day_label(date: dt.date) -> str:
    """
    تنسيق التاريخ بصيغة يوم/شهر/سنة
    
    المعاملات:
        date: كائن التاريخ
    
    العودة:
        النص المنسق (مثل 15/01/2024)
    """
    return date.strftime("%d/%m/%Y")


def format_week_label(date: dt.date) -> str:
    """
    تنسيق تسمية الأسبوع
    
    المعاملات:
        date: كائن التاريخ
    
    العودة:
        النص المنسق (مثل الأسبوع 3 - 2024)
    """
    week = get_iso_week(date)
    return f"الأسبوع {week} - {date.year}"


def apply_date_value(entry: Dict, iso_value: str) -> None:
    """
    تطبيق قيمة التاريخ على الإدخال
    
    المعاملات:
        entry: قاموس بيانات الرابط
        iso_value: قيمة التاريخ بصيغة ISO (YYYY-MM-DD)
    """
    if not iso_value:
        entry['dateValue'] = ''
        entry['dayLabel'] = 'بدون تاريخ'
        entry['weekLabel'] = 'بدون تاريخ'
        return
    
    try:
        date = dt.datetime.strptime(iso_value, "%Y-%m-%d").date()
        entry['dateValue'] = iso_value
        entry['dayLabel'] = format_day_label(date)
        entry['weekLabel'] = format_week_label(date)
    except ValueError:
        entry['dateValue'] = ''
        entry['dayLabel'] = 'بدون تاريخ'
        entry['weekLabel'] = 'بدون تاريخ'


# ══════════════════════════════════════════════════════════════════════════════
# دوال بناء الإدخالات
# ══════════════════════════════════════════════════════════════════════════════

def build_entry(url: str) -> Dict[str, Any]:
    """
    بناء إدخال كامل لرابط واحد
    
    المعاملات:
        url: الرابط المنظف
    
    العودة:
        قاموس يحتوي على كل بيانات الرابط
    """
    # استخراج الوسوم
    tag_info = extract_tag_and_folder(url)
    
    # تحديد النوع
    url_type = classify_url_type(url)
    
    # بناء الإدخال
    entry: Dict[str, Any] = {
        'url': url,
        'tag': tag_info['primaryTag'],
        'folder': tag_info['folder'],
        'siteTag': tag_info['siteTag'],
        'extraTags': '',
        'type': url_type,
        'dateValue': '',
        'dayLabel': 'بدون تاريخ',
        'weekLabel': 'بدون تاريخ',
        'title': '',
    }
    
    # إضافة حقول خاصة بقوائم التشغيل
    if url_type == 'playlist':
        entry['videoCount'] = 0
        entry['totalViews'] = 0
    
    # محاولة استخراج التاريخ من الرابط
    detected_date = detect_date_from_url(url)
    if detected_date:
        apply_date_value(entry, detected_date.isoformat())
    
    return entry


# ══════════════════════════════════════════════════════════════════════════════
# دوال جلب العناوين
# ══════════════════════════════════════════════════════════════════════════════

def fetch_youtube_video_title(url: str) -> Optional[str]:
    """
    جلب عنوان فيديو يوتيوب باستخدام oEmbed API
    
    المعاملات:
        url: رابط الفيديو
    
    العودة:
        عنوان الفيديو أو None
    """
    if not REQUESTS_AVAILABLE:
        return None
    
    try:
        oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
        response = requests.get(oembed_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('title')
        
        return None
        
    except Exception as e:
        log(f"خطأ في جلب عنوان الفيديو: {e}", "WARNING")
        return None


def fetch_youtube_playlist_info(url: str) -> Dict[str, Any]:
    """
    جلب معلومات قائمة تشغيل يوتيوب
    
    المعاملات:
        url: رابط قائمة التشغيل
    
    العودة:
        قاموس يحتوي على: title, videoCount, totalViews
    """
    result = {
        'title': '',
        'videoCount': 0,
        'totalViews': 0,
    }
    
    if not YT_DLP_AVAILABLE:
        return result
    
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'skip_download': True,
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if info:
                result['title'] = info.get('title', '')
                
                # عدد الفيديوهات
                entries = info.get('entries', [])
                result['videoCount'] = len(entries) if entries else info.get('playlist_count', 0)
                
                # محاولة جلب عدد المشاهدات (قد لا يتوفر دائماً)
                result['totalViews'] = info.get('view_count', 0)
        
        return result
        
    except Exception as e:
        log(f"خطأ في جلب معلومات القائمة: {e}", "WARNING")
        return result


def fetch_webpage_title(url: str) -> Optional[str]:
    """
    جلب عنوان صفحة ويب عادية
    
    المعاملات:
        url: رابط الصفحة
    
    العودة:
        عنوان الصفحة أو None
    """
    if not REQUESTS_AVAILABLE or not BS4_AVAILABLE:
        return None
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # البحث عن عنصر title
            title_tag = soup.find('title')
            if title_tag:
                return title_tag.get_text().strip()
            
            # البحث عن og:title
            og_title = soup.find('meta', property='og:title')
            if og_title:
                return og_title.get('content', '').strip()
        
        return None
        
    except Exception as e:
        log(f"خطأ في جلب عنوان الصفحة: {e}", "WARNING")
        return None


def fetch_all_titles(entries: List[Dict], log_file: Optional[Path] = None) -> Tuple[int, int, int]:
    """
    جلب عناوين جميع الروابط
    
    المعاملات:
        entries: قائمة الإدخالات
        log_file: ملف السجل
    
    العودة:
        (عدد المحدّث، عدد المتخطّى، عدد الفاشل)
    """
    updated = 0
    skipped = 0
    failed = 0
    
    total = len(entries)
    
    for i, entry in enumerate(entries, 1):
        url = entry.get('url', '')
        url_type = entry.get('type', '')
        site_tag = entry.get('siteTag', '')
        current_title = entry.get('title', '')
        
        # تخطي إذا العنوان موجود
        if current_title:
            skipped += 1
            continue
        
        log(f"[{i}/{total}] جلب عنوان: {url[:50]}...", log_file=log_file)
        
        title = None
        
        # فيديوهات وشورتس يوتيوب
        if site_tag == '#youtube' and url_type in ('video', 'short'):
            title = fetch_youtube_video_title(url)
        
        # قوائم التشغيل
        elif site_tag == '#youtube' and url_type == 'playlist':
            playlist_info = fetch_youtube_playlist_info(url)
            title = playlist_info.get('title')
            entry['videoCount'] = playlist_info.get('videoCount', 0)
            entry['totalViews'] = playlist_info.get('totalViews', 0)
        
        # صفحات الويب الأخرى
        elif url_type == 'webpage':
            title = fetch_webpage_title(url)
        
        if title:
            entry['title'] = title
            updated += 1
            log(f"   ✓ {title[:50]}...", "SUCCESS", log_file)
        else:
            failed += 1
            log(f"   ✗ فشل جلب العنوان", "WARNING", log_file)
    
    return updated, skipped, failed


# ══════════════════════════════════════════════════════════════════════════════
# دوال قراءة وكتابة الملفات
# ══════════════════════════════════════════════════════════════════════════════

def load_urls_from_txt(file_path: Path) -> List[str]:
    """
    قراءة الروابط من ملف نصي
    
    المعاملات:
        file_path: مسار الملف
    
    العودة:
        قائمة الروابط النظيفة
    """
    if not file_path.exists():
        raise FileNotFoundError(f"الملف غير موجود: {file_path}")
    
    urls = []
    with file_path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # تجاهل السطور الفارغة والتعليقات
            if line and not line.startswith('#'):
                urls.append(line)
    
    return urls


def save_urls_to_txt(urls: List[str], file_path: Path) -> None:
    """
    حفظ الروابط في ملف نصي
    
    المعاملات:
        urls: قائمة الروابط
        file_path: مسار الملف
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with file_path.open('w', encoding='utf-8') as f:
        for url in urls:
            f.write(url + '\n')
    
    log(f"تم حفظ {len(urls)} رابط في {file_path}", "SUCCESS")


def load_entries_from_json(file_path: Path) -> List[Dict]:
    """
    قراءة الإدخالات من ملف JSON
    
    المعاملات:
        file_path: مسار الملف
    
    العودة:
        قائمة الإدخالات
    """
    if not file_path.exists():
        return []
    
    try:
        with file_path.open('r', encoding='utf-8') as f:
            data = json.load(f)
        
        # دعم الصيغة القديمة (مصفوفة مباشرة) والجديدة (كائن مع entries)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'entries' in data:
            return data['entries']
        else:
            return []
            
    except json.JSONDecodeError as e:
        log(f"خطأ في قراءة ملف JSON: {e}", "ERROR")
        return []


def save_entries_to_json(entries: List[Dict], file_path: Path) -> None:
    """
    حفظ الإدخالات في ملف JSON
    
    المعاملات:
        entries: قائمة الإدخالات
        file_path: مسار الملف
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    payload = {
        'generatedAt': dt.datetime.now().isoformat(),
        'total': len(entries),
        'entries': entries,
    }
    
    with file_path.open('w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    
    log(f"تم حفظ {len(entries)} إدخال في {file_path}", "SUCCESS")


# ══════════════════════════════════════════════════════════════════════════════
# دوال التحميل
# ══════════════════════════════════════════════════════════════════════════════

def build_ydl_opts(output_dir: Path, fmt: str, write_metadata: bool = True) -> Dict:
    """
    بناء خيارات yt-dlp
    
    المعاملات:
        output_dir: مجلد الإخراج
        fmt: صيغة التحميل
        write_metadata: حفظ الميتاداتا أم لا
    
    العودة:
        قاموس الإعدادات
    """
    outtmpl = str(output_dir / "%(uploader)s/%(upload_date)s - %(title)s [%(id)s].%(ext)s")
    
    ydl_opts: Dict = {
        'outtmpl': outtmpl,
        'format': fmt,
        'noplaylist': False,
        'ignoreerrors': True,
        'retries': 5,
        'fragment_retries': 10,
        'concurrent_fragment_downloads': 5,
        'merge_output_format': 'mp4',
        'continuedl': True,
        'noprogress': False,
    }
    
    if write_metadata:
        ydl_opts.update({
            'writeinfojson': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'writethumbnail': True,
        })
    
    return ydl_opts


def download_one(
    index: int,
    url: str,
    output_dir: Path,
    fmt: str,
    log_file: Path,
    write_metadata: bool = True
) -> bool:
    """
    تحميل فيديو/قائمة واحدة
    
    المعاملات:
        index: رقم الفيديو في القائمة
        url: رابط الفيديو
        output_dir: مجلد الإخراج
        fmt: صيغة التحميل
        log_file: ملف السجل
        write_metadata: حفظ الميتاداتا
    
    العودة:
        True إذا نجح، False إذا فشل
    """
    if not YT_DLP_AVAILABLE:
        log(f"[{index}] yt-dlp غير مثبت، تخطي: {url}", "WARNING", log_file)
        return False
    
    try:
        log(f"[{index}] بدء التحميل: {url}", log_file=log_file)
        ydl_opts = build_ydl_opts(output_dir, fmt, write_metadata)
        
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        log(f"[{index}] تم التحميل بنجاح", "SUCCESS", log_file)
        return True
        
    except Exception as e:
        log(f"[{index}] فشل التحميل: {url} | الخطأ: {e}", "ERROR", log_file)
        return False


def download_all(
    entries: List[Dict],
    output_dir: Path,
    fmt: str,
    max_concurrent: int,
    log_file: Path,
    write_metadata: bool = True
) -> Tuple[int, int]:
    """
    تحميل جميع الفيديوهات
    
    المعاملات:
        entries: قائمة الإدخالات
        output_dir: مجلد الإخراج
        fmt: صيغة التحميل
        max_concurrent: أقصى عدد تحميلات متوازية
        log_file: ملف السجل
        write_metadata: حفظ الميتاداتا
    
    العودة:
        (عدد الناجح، عدد الفاشل)
    """
    success = 0
    failed = 0
    
    # فلترة الروابط القابلة للتحميل (يوتيوب فقط)
    downloadable = [
        e for e in entries
        if e.get('siteTag') == '#youtube'
    ]
    
    if not downloadable:
        log("لا توجد روابط يوتيوب قابلة للتحميل.", "WARNING", log_file)
        return 0, 0
    
    log(f"بدء تحميل {len(downloadable)} رابط...", log_file=log_file)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent) as executor:
        futures = {}
        
        for i, entry in enumerate(downloadable, 1):
            url = entry.get('url', '')
            folder = entry.get('folder', 'videos')
            
            # إنشاء مجلد فرعي حسب التصنيف
            entry_output = output_dir / folder
            
            future = executor.submit(
                download_one, i, url, entry_output, fmt, log_file, write_metadata
            )
            futures[future] = url
        
        for future in concurrent.futures.as_completed(futures):
            if future.result():
                success += 1
            else:
                failed += 1
    
    log(f"انتهى التحميل: {success} نجاح، {failed} فشل", log_file=log_file)
    return success, failed


# ══════════════════════════════════════════════════════════════════════════════
# الدالة الرئيسية
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    """الدالة الرئيسية للبرنامج"""
    
    # ═══════════════════════════════════════════════════════════════════
    # إعداد معالج سطر الأوامر
    # ═══════════════════════════════════════════════════════════════════
    
    parser = argparse.ArgumentParser(
        description="أداة أرشفة فيديوهات يوتيوب المتقدمة",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
أمثلة الاستخدام:
─────────────────
  # تنظيف وتصنيف الروابط من ملف نصي
  python youtube_archiver_full.py --urls-file urls.txt --classify-only

  # جلب العناوين من الإنترنت
  python youtube_archiver_full.py --json-file links_data.json --fetch-titles

  # تحميل الفيديوهات
  python youtube_archiver_full.py --json-file links_data.json --download --output-dir ./archive

  # تحميل مع إعدادات مخصصة
  python youtube_archiver_full.py --json-file links_data.json --download \\
      --output-dir ./archive --max-concurrent 4 --format "bestvideo[height<=1080]+bestaudio"
        """
    )
    
    # ═══════════════════════════════════════════════════════════════════
    # خيارات الإدخال
    # ═══════════════════════════════════════════════════════════════════
    
    input_group = parser.add_argument_group("خيارات الإدخال")
    
    input_group.add_argument(
        "--urls-file",
        type=Path,
        help="ملف الروابط النصي (كل سطر رابط)"
    )
    
    input_group.add_argument(
        "--json-file",
        type=Path,
        default=Path("links_data.json"),
        help="ملف JSON للبيانات (افتراضي: links_data.json)"
    )
    
    # ═══════════════════════════════════════════════════════════════════
    # خيارات العمليات
    # ═══════════════════════════════════════════════════════════════════
    
    action_group = parser.add_argument_group("العمليات")
    
    action_group.add_argument(
        "--classify-only",
        action="store_true",
        help="تنظيف وتصنيف الروابط فقط (بدون تحميل)"
    )
    
    action_group.add_argument(
        "--fetch-titles",
        action="store_true",
        help="جلب عناوين الفيديوهات من الإنترنت"
    )
    
    action_group.add_argument(
        "--download",
        action="store_true",
        help="تحميل الفيديوهات"
    )
    
    # ═══════════════════════════════════════════════════════════════════
    # خيارات التحميل
    # ═══════════════════════════════════════════════════════════════════
    
    download_group = parser.add_argument_group("خيارات التحميل")
    
    download_group.add_argument(
        "--output-dir",
        type=Path,
        default=Path("archive"),
        help="مجلد الأرشيف (افتراضي: archive)"
    )
    
    download_group.add_argument(
        "--max-concurrent",
        type=int,
        default=2,
        help="أقصى عدد تحميلات متوازية (افتراضي: 2)"
    )
    
    download_group.add_argument(
        "--format",
        default="bestvideo+bestaudio/best",
        help="صيغة التحميل (افتراضي: bestvideo+bestaudio/best)"
    )
    
    download_group.add_argument(
        "--no-metadata",
        action="store_true",
        help="عدم حفظ الميتاداتا (JSON, ترجمة, صورة)"
    )
    
    # ═══════════════════════════════════════════════════════════════════
    # معالجة الخيارات
    # ═══════════════════════════════════════════════════════════════════
    
    args = parser.parse_args()
    
    # التحقق من وجود عملية محددة
    if not any([args.classify_only, args.fetch_titles, args.download]):
        parser.print_help()
        print("\n[!] يجب تحديد عملية واحدة على الأقل:")
        print("    --classify-only  أو  --fetch-titles  أو  --download")
        sys.exit(1)
    
    # إعداد ملف السجل
    log_dir = args.output_dir if args.download else Path(".")
    log_file = log_dir / "archiver.log"
    
    # ═══════════════════════════════════════════════════════════════════
    # تحميل أو إنشاء البيانات
    # ═══════════════════════════════════════════════════════════════════
    
    entries: List[Dict] = []
    
    # إذا تم تحديد ملف روابط نصي
    if args.urls_file:
        print_header("قراءة الروابط من ملف نصي")
        
        try:
            raw_urls = load_urls_from_txt(args.urls_file)
            log(f"تم قراءة {len(raw_urls)} رابط من {args.urls_file}")
            
            # تنظيف وتصنيف الروابط
            seen = set()
            for url in raw_urls:
                cleaned = clean_url(url)
                if cleaned and cleaned not in seen:
                    seen.add(cleaned)
                    entry = build_entry(cleaned)
                    entries.append(entry)
            
            log(f"تم تنظيف وتصنيف {len(entries)} رابط فريد", "SUCCESS")
            
        except FileNotFoundError as e:
            log(str(e), "ERROR")
            sys.exit(1)
    
    # تحميل من ملف JSON الموجود
    elif args.json_file.exists():
        print_header("تحميل البيانات من ملف JSON")
        entries = load_entries_from_json(args.json_file)
        log(f"تم تحميل {len(entries)} إدخال من {args.json_file}")
    
    else:
        log(f"ملف JSON غير موجود: {args.json_file}", "ERROR")
        log("استخدم --urls-file لإنشاء ملف جديد من روابط نصية")
        sys.exit(1)
    
    # ═══════════════════════════════════════════════════════════════════
    # عرض الإحصائيات
    # ═══════════════════════════════════════════════════════════════════
    
    print_stats(entries)
    
    # ═══════════════════════════════════════════════════════════════════
    # جلب العناوين
    # ═══════════════════════════════════════════════════════════════════
    
    if args.fetch_titles:
        print_header("جلب العناوين من الإنترنت")
        updated, skipped, failed = fetch_all_titles(entries, log_file)
        log(f"النتيجة: {updated} محدّث، {skipped} متخطّى، {failed} فاشل", "SUCCESS")
    
    # ═══════════════════════════════════════════════════════════════════
    # حفظ البيانات
    # ═══════════════════════════════════════════════════════════════════
    
    if args.classify_only or args.fetch_titles:
        print_header("حفظ البيانات")
        save_entries_to_json(entries, args.json_file)
        
        # حفظ ملف urls.txt أيضاً
        urls_file = args.json_file.with_suffix('.txt')
        save_urls_to_txt([e['url'] for e in entries], urls_file)
    
    # ═══════════════════════════════════════════════════════════════════
    # تحميل الفيديوهات
    # ═══════════════════════════════════════════════════════════════════
    
    if args.download:
        print_header("تحميل الفيديوهات")
        
        # إنشاء مجلد الأرشيف
        args.output_dir.mkdir(parents=True, exist_ok=True)
        
        success, failed = download_all(
            entries=entries,
            output_dir=args.output_dir,
            fmt=args.format,
            max_concurrent=max(1, args.max_concurrent),
            log_file=log_file,
            write_metadata=not args.no_metadata
        )
        
        log(f"اكتملت عملية الأرشفة: {success} نجاح، {failed} فشل", "SUCCESS", log_file)
    
    # ═══════════════════════════════════════════════════════════════════
    # النهاية
    # ═══════════════════════════════════════════════════════════════════
    
    print_header("انتهى البرنامج")
    log("شكراً لاستخدام أداة أرشفة يوتيوب!", "SUCCESS")


# ══════════════════════════════════════════════════════════════════════════════
# نقطة الدخول
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()
