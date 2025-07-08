import json
import os
import pytz

# Timezone ayarları için dosya
TIMEZONE_CONFIG_FILE = 'timezone_settings.json'

# Popüler timezone'lar listesi
POPULAR_TIMEZONES = [
    ('Europe/Istanbul', 'İstanbul (UTC+3)'),
    ('Europe/London', 'Londra (UTC+0)'),
    ('America/New_York', 'New York (UTC-5)'),
    ('America/Los_Angeles', 'Los Angeles (UTC-8)'),
    ('Asia/Tokyo', 'Tokyo (UTC+9)'),
    ('Asia/Shanghai', 'Şangay (UTC+8)'),
    ('Europe/Berlin', 'Berlin (UTC+1)'),
    ('Europe/Paris', 'Paris (UTC+1)'),
    ('Asia/Dubai', 'Dubai (UTC+4)'),
    ('Australia/Sydney', 'Sidney (UTC+10)'),
    ('UTC', 'UTC (Koordinatlı Evrensel Zaman)'),
]

def get_all_timezones():
    """Tüm pytz timezone'larını alfabetik sırada döndürür"""
    return sorted(pytz.all_timezones)

def get_popular_timezones():
    """Popüler timezone'ları döndürür"""
    return POPULAR_TIMEZONES

def get_default_timezone():
    """Varsayılan timezone'ı döndürür"""
    return 'Europe/Istanbul'

def load_timezone_config():
    """Timezone ayarlarını dosyadan yükler"""
    try:
        if os.path.exists(TIMEZONE_CONFIG_FILE):
            with open(TIMEZONE_CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config
        else:
            # Varsayılan ayarlar
            return {
                'timezone': get_default_timezone(),
                'display_format': '%d.%m.%Y %H:%M',
                'date_format': '%d.%m.%Y',
                'time_format': '%H:%M'
            }
    except Exception as e:
        print(f"Timezone config yükleme hatası: {e}")
        return {
            'timezone': get_default_timezone(),
            'display_format': '%d.%m.%Y %H:%M',
            'date_format': '%d.%m.%Y',
            'time_format': '%H:%M'
        }

def save_timezone_config(config_data):
    """Timezone ayarlarını dosyaya kaydeder"""
    try:
        with open(TIMEZONE_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Timezone config kaydetme hatası: {e}")
        return False

def get_current_timezone():
    """Şu anki timezone ayarını döndürür"""
    config = load_timezone_config()
    return config.get('timezone', get_default_timezone())

def validate_timezone(timezone_str):
    """Timezone'ın geçerli olup olmadığını kontrol eder"""
    try:
        pytz.timezone(timezone_str)
        return True
    except pytz.exceptions.UnknownTimeZoneError:
        return False
