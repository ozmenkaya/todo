#!/bin/bash

# 🌊 DigitalOcean App Platform Deployment Script
# Bu script GitHub repo'yu hazırlar ve DigitalOcean deployment'ı için rehber verir

echo "🌊 DigitalOcean App Platform Deployment Başlıyor..."

# Git kontrolü
if ! command -v git &> /dev/null; then
    echo "❌ Git bulunamadı. Lütfen yükleyin."
    exit 1
fi

# GitHub repository bilgilerini al
echo "📝 GitHub repository bilgilerini girin:"
read -p "GitHub kullanıcı adınız: " GITHUB_USERNAME
read -p "Repository adı (örn: todo-app): " REPO_NAME

if [ -z "$GITHUB_USERNAME" ] || [ -z "$REPO_NAME" ]; then
    echo "❌ GitHub bilgileri gerekli!"
    exit 1
fi

# App.yaml dosyasını güncelle
echo "🔧 App.yaml dosyası güncelleniyor..."
sed -i.bak "s/your-username/$GITHUB_USERNAME/g" .do/app.yaml
sed -i.bak "s/your-repo-name/$REPO_NAME/g" .do/app.yaml
rm -f .do/app.yaml.bak

# Secret key oluştur
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
sed -i.bak "s/change-this-to-a-secure-secret-key-12345/$SECRET_KEY/g" .do/app.yaml
rm -f .do/app.yaml.bak

echo "✅ App.yaml dosyası güncellendi!"

# GitHub remote ekle
echo "📦 GitHub remote ekleniyor..."
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/$GITHUB_USERNAME/$REPO_NAME.git

# Git commit ve push
echo "🚀 Kod GitHub'a gönderiliyor..."
git add .
git commit -m "Add DigitalOcean deployment configuration"
git branch -M main

echo ""
echo "🔑 GitHub Personal Access Token ile push yapın:"
echo "   git push -u origin main"
echo ""
echo "   Token oluşturmak için: https://github.com/settings/tokens"
echo "   Yetkiler: repo (full access)"
echo ""

# DigitalOcean rehberi
echo "🌊 DigitalOcean App Platform'da deployment:"
echo ""
echo "1. 🔗 https://cloud.digitalocean.com/apps adresine gidin"
echo "2. 📱 'Create App' butonuna tıklayın"
echo "3. 🐙 GitHub'ı seçin ve '$GITHUB_USERNAME/$REPO_NAME' repo'sunu bağlayın"
echo "4. 🔧 Branch olarak 'main' seçin"
echo "5. ⚡ 'Autodeploy' aktif tutun"
echo "6. 💾 '.do/app.yaml' dosyası otomatik algılanacak"
echo "7. 🎯 'Create Resources' ile deploy edin"
echo ""
echo "💰 Tahmini maliyet: \$5/ay (Basic plan)"
echo "🌐 URL: https://todo-management-app-xxxxx.ondigitalocean.app"
echo "🔑 Admin girişi: admin / admin123"
echo ""
echo "🎉 5-10 dakika içinde uygulamanız hazır olacak!"
echo ""

# Push işlemi için konfirmasyon
read -p "📤 Şimdi GitHub'a push yapmak ister misiniz? (y/N): " PUSH_NOW
if [[ $PUSH_NOW =~ ^[Yy]$ ]]; then
    echo "🚀 GitHub'a push yapılıyor..."
    git push -u origin main
    
    if [ $? -eq 0 ]; then
        echo "✅ GitHub'a başarıyla gönderildi!"
        echo "🌊 Şimdi DigitalOcean'da app oluşturabilirsiniz!"
        
        # Tarayıcıda aç
        read -p "🔗 DigitalOcean Apps sayfasını tarayıcıda açmak ister misiniz? (y/N): " OPEN_DO
        if [[ $OPEN_DO =~ ^[Yy]$ ]]; then
            open "https://cloud.digitalocean.com/apps"
        fi
    else
        echo "❌ Push başarısız. Personal Access Token kullandığınızdan emin olun."
        echo "💡 Tip: GitHub → Settings → Developer settings → Personal access tokens"
    fi
fi

echo ""
echo "📖 Detaylı rehber için: cat DIGITALOCEAN_DEPLOYMENT.md"
