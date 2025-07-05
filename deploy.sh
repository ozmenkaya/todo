#!/bin/bash

# 🚀 Todo App Deployment Script
# Bu script projenizi Heroku'ya hızlıca deploy eder

echo "🚀 Todo Uygulaması Deployment Başlıyor..."

# Heroku CLI kontrolü
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI bulunamadı. Lütfen yükleyin: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Git kontrolü
if ! command -v git &> /dev/null; then
    echo "❌ Git bulunamadı. Lütfen yükleyin."
    exit 1
fi

# Uygulama adını sor
read -p "📝 Heroku app adını girin (örn: my-todo-app): " APP_NAME

if [ -z "$APP_NAME" ]; then
    echo "❌ App adı gerekli!"
    exit 1
fi

echo "🔧 Heroku app oluşturuluyor..."
heroku create $APP_NAME

if [ $? -ne 0 ]; then
    echo "❌ App oluşturulamadı. Farklı bir isim deneyin."
    exit 1
fi

echo "🔐 Environment variables ayarlanıyor..."
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(16))')
heroku config:set SECRET_KEY="$SECRET_KEY" --app $APP_NAME
heroku config:set FLASK_ENV="production" --app $APP_NAME

echo "📦 Deploy ediliyor..."
git push heroku main

if [ $? -eq 0 ]; then
    echo "✅ Deploy başarılı!"
    echo "🌐 Uygulamanız şu adreste: https://$APP_NAME.herokuapp.com"
    echo "🔑 Admin girişi: admin / admin123"
    echo ""
    echo "🎉 Tebrikler! Uygulamanız artık internette!"
    
    # Tarayıcıda aç
    read -p "📱 Tarayıcıda açmak ister misiniz? (y/N): " OPEN_BROWSER
    if [[ $OPEN_BROWSER =~ ^[Yy]$ ]]; then
        heroku open --app $APP_NAME
    fi
else
    echo "❌ Deploy başarısız. Lütfen hataları kontrol edin."
    exit 1
fi
