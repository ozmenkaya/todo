# 🚀 DigitalOcean Deployment Rehberi

## 📋 Önkoşullar
- DigitalOcean hesabı
- Gmail App Password (mail sistemi için)
- GitHub repository: `ozmenkaya/todo`

## 🔧 Deployment Adımları

### 1️⃣ DigitalOcean App Platform'a Git
- [DigitalOcean Control Panel](https://cloud.digitalocean.com) → Apps

### 2️⃣ Yeni App Oluştur
- "Create App" butonuna tıkla
- "GitHub" seçeneğini seç
- Repository: `ozmenkaya/todo`
- Branch: `main`
- Source Directory: `/` (root)

### 3️⃣ App Spec'i Yükle
- "Edit App Spec" sekmesine git
- Mevcut spec'i sil ve şu içeriği yapıştır:

```yaml
name: helmex-todo-app
services:
- name: web
  source_dir: /
  github:
    repo: ozmenkaya/todo
    branch: main
    deploy_on_push: true
  build_command: pip install -r requirements.txt
  run_command: python start_app.py
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  http_port: 8080
  envs:
  - key: SECRET_KEY
    value: f207c647dae4dd859b20bf29a98b82086f5b3e00c078bcafd35d622781b0200a
  - key: FLASK_ENV
    value: production
  - key: PORT
    value: "8080"
  - key: DATABASE_URL
    value: ${helmex-todo-db.DATABASE_URL}
  - key: MAIL_SERVER
    value: smtp.gmail.com
  - key: MAIL_PORT
    value: "587"
  - key: MAIL_USE_TLS
    value: "true"
  - key: MAIL_USERNAME
    value: info@helmex.com.tr
  - key: MAIL_PASSWORD
    value: YOUR_GMAIL_APP_PASSWORD_HERE
  - key: MAIL_DEFAULT_SENDER
    value: noreply@helmex.com.tr

databases:
- name: helmex-todo-db
  engine: PG
  size: db-s-dev-database
  num_nodes: 1
```

### 4️⃣ Environment Variables Güncelle
**ÖNEMLİ**: `MAIL_PASSWORD` değerini Gmail App Password'unuzla değiştirin!

### 5️⃣ Deploy Et
- "Next" → "Next" → "Create Resources"
- Deployment başlayacak (5-10 dakika sürer)

## 📧 Deployment Sonrası

### ✅ Test Edilecekler:
1. **App URL'si** çalışıyor mu?
2. **PostgreSQL** bağlantısı var mı?
3. **Admin Login**: `admin` / `admin123`
4. **Mail sistemi** çalışıyor mu?
5. **Görev oluşturma** ve **acil mail** gönderimi

### 🔧 İlk Kurulum:
1. Admin olarak giriş yap
2. Mail ayarlarını kontrol et: `/admin/mail-settings`
3. Test mail gönder
4. Kullanıcıları ekle: `/add_user`
5. Test görevleri oluştur

## 🌐 Production URL
Deployment tamamlandıktan sonra DigitalOcean size şu formatta URL verecek:
`https://helmex-todo-app-xxxxx.ondigitalocean.app`

## 💰 Tahmini Maliyet
- **Web App**: $5/ay (Basic Plan)
- **PostgreSQL DB**: $15/ay (Development Database)
- **Toplam**: ~$20/ay

## 🔐 Güvenlik Notları
- Production'da SECRET_KEY'i değiştirin
- MAIL_PASSWORD'u güncel tutun
- Database backup'larını düzenli alın

## 🆘 Sorun Giderme
- **Build hatası**: Requirements.txt'yi kontrol edin
- **Database hatası**: CONNECTION_URL'i kontrol edin
- **Mail hatası**: Gmail App Password'u kontrol edin
- **404 hatası**: start_app.py dosyasının mevcut olduğunu kontrol edin

## 📱 Domain Bağlama (Opsiyonel)
Custom domain bağlamak için:
1. DigitalOcean Apps → Settings → Domains
2. Domain ekle: `todo.helmex.com.tr`
3. DNS ayarlarını yapılandır

Deployment başarılı olduktan sonra production URL'ini paylaşabilirsiniz! 🎉
