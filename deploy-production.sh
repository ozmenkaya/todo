#!/bin/bash

# 🚀 Production Deployment Script
# Bu script uygulamayı production modda başlatır

echo "🚀 Production Deployment Başlıyor..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 bulunamadı!"
    exit 1
fi

# Check requirements
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt bulunamadı!"
    exit 1
fi

echo "📦 Virtual environment kontrol ediliyor..."
if [ ! -d ".venv" ]; then
    echo "🔧 Virtual environment oluşturuluyor..."
    python3 -m venv .venv
fi

echo "🔧 Virtual environment aktifleştiriliyor..."
source .venv/bin/activate

echo "📥 Dependencies yükleniyor..."
pip install -r requirements.txt

echo "🔐 Production environment ayarlanıyor..."
export FLASK_ENV=production
export DEBUG=False
export PORT=5004

# Secret key oluştur
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
export SECRET_KEY="$SECRET_KEY"

# OneSignal konfigürasyonu
export ONESIGNAL_APP_ID="0047e2bf-7209-4b1c-b222-310e700a9780"
export ONESIGNAL_API_KEY="os_v2_app_abd6fp3sbffrzmrcgehhacuxqcalxza3656u4p5gzxpcmji55xmckrxansybtyo6nvii2pq2onkoguolsra7lj6j3thkrq5sijnesvy"
export ONESIGNAL_APNS_TEAM_ID="435XR8VR9X"
export ONESIGNAL_APNS_BUNDLE_ID="com.helmex"

echo "📱 OneSignal konfigürasyonu ayarlandı!"

echo "🗄️ Database hazırlanıyor..."
python3 -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('✅ Database tabloları oluşturuldu')
"

echo "👤 Admin kullanıcı kontrol ediliyor..."
python3 -c "
from app import app, create_admin_user
with app.app_context():
    create_admin_user()
    print('✅ Admin kullanıcı hazır')
"

# Development server'ı durdur
echo "🛑 Development server'ları durduruyor..."
pkill -f "python.*start_app.py" 2>/dev/null || true
pkill -f "flask.*run" 2>/dev/null || true

echo "🌐 Production server başlatılıyor..."
echo "📍 URL: http://localhost:5004"
echo "🔑 Admin: admin / admin123"
echo ""
echo "🔧 Server başlatma komutları:"
echo "   1️⃣ Flask development: FLASK_ENV=production python start_app.py"
echo "   2️⃣ Gunicorn (önerilen): gunicorn --bind 0.0.0.0:5004 --workers 4 app:app"
echo "   3️⃣ Docker: docker-compose up -d"
echo ""

# Gunicorn kontrolü
if command -v gunicorn &> /dev/null; then
    echo "🚀 Gunicorn ile başlatılıyor..."
    gunicorn --bind 0.0.0.0:5004 --workers 2 --timeout 120 --keepalive 2 app:app
else
    echo "🚀 Flask ile başlatılıyor..."
    FLASK_ENV=production python start_app.py
fi
