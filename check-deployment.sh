#!/bin/bash

echo "🔍 DigitalOcean Deployment Status Checker"
echo "========================================"
echo

echo "📊 Son Yapılan Değişiklikler:"
echo "----------------------------"
echo "✅ Requirements.txt: Sadece Flask essentials"
echo "✅ App.yaml: Python app.py komutu"
echo "✅ Procfile: web: python app.py"
echo "✅ PORT environment variable: 8080"
echo

echo "📦 Şu Anki Requirements:"
echo "----------------------"
cat requirements.txt
echo

echo "⚙️ Şu Anki App.yaml Run Command:"
echo "------------------------------"
grep "run_command:" .do/app.yaml
echo

echo "🧪 Test Apps:"
echo "------------"
echo "1. Simple Test App: simple_app.py (✅ Local test başarılı)"
echo "2. Main App: app.py"
echo

echo "🎯 Deployment Durumu:"
echo "--------------------"
echo "URL: https://seashell-app-ji9wm.ondigitalocean.app/"
echo "Son Push: $(git log -1 --format='%cd' --date=short) $(git log -1 --format='%H' | head -c 7)"
echo "Son Commit: $(git log -1 --format='%s')"
echo

echo "⏱️ Bekleme Süresi:"
echo "------------------"
echo "DigitalOcean rebuild: ~3-5 dakika"
echo "Şu anki zaman: $(date)"
echo

echo "🔧 Manuel Kontrol Adımları:"
echo "--------------------------"
echo "1. DigitalOcean Dashboard'a git: https://cloud.digitalocean.com/apps"
echo "2. 'todo-management-app' bulun"
echo "3. 'Activity' tab'ında build logs'u kontrol edin"
echo "4. 'Runtime Logs' kontrol edin"
echo "5. Gerekirse 'Force Rebuild' yapın"
echo

# URL test
echo "🌐 URL Test:"
echo "------------"
if curl -s --max-time 10 https://seashell-app-ji9wm.ondigitalocean.app/ | grep -q "html\|json\|error" 2>/dev/null; then
    echo "✅ URL'ye erişim var (content var)"
else
    echo "❌ URL'ye erişim yok veya 404"
fi
echo

echo "🎪 Eğer Hala 404 Alırsanız:"
echo "--------------------------"
echo "Plan B: Yeni app oluşturun"
echo "1. DigitalOcean'da 'Create New App'"
echo "2. GitHub: ozmenkaya/todo"
echo "3. Branch: main"
echo "4. Import app spec: .do/app-test.yaml (simple version)"
echo

echo "📞 Support:"
echo "----------"
echo "DigitalOcean Support: https://cloud.digitalocean.com/support/tickets"
echo "Community: https://www.digitalocean.com/community"
