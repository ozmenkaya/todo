#!/bin/bash

# 🔧 DigitalOcean No Component Detected Troubleshooting

echo "🔍 DigitalOcean Component Detection Sorun Gideric"
echo "=============================================="

echo ""
echo "📁 Dosya Kontrolleri:"
echo "===================="

# Requirements.txt kontrol
if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt mevcut"
    echo "📦 İçerik:"
    head -5 requirements.txt
else
    echo "❌ requirements.txt bulunamadı!"
fi

echo ""

# Runtime.txt kontrol
if [ -f "runtime.txt" ]; then
    echo "✅ runtime.txt mevcut: $(cat runtime.txt)"
else
    echo "❌ runtime.txt bulunamadı!"
fi

echo ""

# App.py kontrol
if [ -f "app.py" ]; then
    echo "✅ app.py mevcut"
else
    echo "❌ app.py bulunamadı!"
fi

echo ""

# App.yaml kontrol
if [ -f ".do/app.yaml" ]; then
    echo "✅ .do/app.yaml mevcut"
    echo "📝 Repository config:"
    grep -A 3 "github:" .do/app.yaml
else
    echo "❌ .do/app.yaml bulunamadı!"
fi

echo ""
echo "🛠️ Önerilen Çözümler:"
echo "==================="
echo ""
echo "1. 📂 GitHub Repository Formatı:"
echo "   Doğru: 'username/repo-name'"
echo "   Yanlış: 'username@email.com/repo-name'"
echo ""
echo "2. 📋 Gerekli Dosyalar:"
echo "   ✓ requirements.txt"
echo "   ✓ runtime.txt (Python version)"
echo "   ✓ app.py (main application)"
echo "   ✓ .do/app.yaml (config)"
echo ""
echo "3. 🔧 DigitalOcean'da Manuel Kurulum:"
echo "   - Source: GitHub"
echo "   - Build Command: pip install -r requirements.txt"
echo "   - Run Command: python app.py"
echo "   - Environment: Python"
echo ""
echo "4. 🎯 Alternative Yaklaşım:"
echo "   - App.yaml dosyasını silip manuel setup yapın"
echo "   - DigitalOcean'ın auto-detection özelliğini kullanın"
echo ""

# GitHub repo kontrol
echo "🐙 GitHub Repository Kontrolü:"
echo "=============================="
if git remote get-url origin 2>/dev/null; then
    REPO_URL=$(git remote get-url origin)
    echo "📍 Remote URL: $REPO_URL"
    
    # Extract username/repo from URL
    if [[ $REPO_URL == *"github.com"* ]]; then
        REPO_PATH=$(echo $REPO_URL | sed 's/.*github.com[:/]//' | sed 's/\.git$//')
        echo "📁 Repository Path: $REPO_PATH"
        echo ""
        echo "💡 App.yaml'da kullanın: repo: $REPO_PATH"
    fi
else
    echo "❌ Git remote origin bulunamadı!"
fi

echo ""
echo "🚀 Hızlı Çözüm:"
echo "==============="
echo "1. GitHub'da repository'nin public olduğundan emin olun"
echo "2. .do/app-simple.yaml dosyasını .do/app.yaml olarak kopyalayın"
echo "3. DigitalOcean'da 'Import from GitHub' yerine manuel setup yapın"
echo ""
