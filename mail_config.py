"""
Mail konfigürasyonu için kalıcı saklama sistemi
"""
import json
import os
from typing import Dict, Any

MAIL_CONFIG_FILE = 'mail_settings.json'

def save_mail_config(config_data: Dict[str, Any]) -> bool:
    """Mail ayarlarını dosyaya kaydet"""
    try:
        with open(MAIL_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Mail konfigürasyonu kaydedilemedi: {e}")
        return False

def load_mail_config() -> Dict[str, Any]:
    """Dosyadan mail ayarlarını yükle"""
    try:
        if os.path.exists(MAIL_CONFIG_FILE):
            with open(MAIL_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"❌ Mail konfigürasyonu yüklenemedi: {e}")
    
    # Varsayılan değerler
    return {
        'MAIL_SERVER': 'smtp.gmail.com',
        'MAIL_PORT': 587,
        'MAIL_USE_TLS': True,
        'MAIL_USERNAME': '',
        'MAIL_PASSWORD': '',
        'MAIL_DEFAULT_SENDER': 'noreply@helmex.com'
    }

def apply_mail_config_to_app(app, config_data: Dict[str, Any]):
    """Mail konfigürasyonunu Flask app'e uygula"""
    try:
        for key, value in config_data.items():
            if key.startswith('MAIL_'):
                app.config[key] = value
        print(f"✅ Mail konfigürasyonu uygulandı: {config_data.get('MAIL_SERVER', 'N/A')}")
        return True
    except Exception as e:
        print(f"❌ Mail konfigürasyonu uygulanamadı: {e}")
        return False
