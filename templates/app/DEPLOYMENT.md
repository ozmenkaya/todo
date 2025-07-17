# 🚀 Company Task Management System - Deployment Guide

Bu rehber, Şirket Görev Yönetim Sistemi'ni production ortamında deploy etmek için gereken adımları içerir.

## 📋 Gereksinimler

- **Docker** ve **Docker Compose**
- **Node.js** (v18+) ve **npm** (frontend build için)
- **Python** (v3.11+) (manuel deployment için)

## 🚀 Hızlı Deployment (Docker ile)

### 1. Otomatik Deploy

```bash
./deploy.sh
```

Bu script otomatik olarak:
- Mevcut container'ları durdurur
- Yeni image build eder
- Container'ları başlatır
- Health check yapar

### 2. Manuel Docker Deploy

```bash
# Image build et
docker-compose build

# Container'ları başlat
docker-compose up -d

# Logları görüntüle
docker-compose logs -f
```

## 🏗️ Manuel Deployment

### Frontend Build

```bash
# Dependencies'leri yükle
npm install

# Production build
npm run build

# Build dosyaları dist/ klasöründe olacak
```

### Backend Setup

```bash
cd backend

# Virtual environment oluştur
python -m venv venv
source venv/bin/activate

# Dependencies'leri yükle
pip install -r requirements.txt

# Production ortamında başlat
./start-production.sh
```

## 🔧 Konfigürasyon

### Environment Variables

Backend için `.env.production` dosyasını düzenleyin:

```env
FLASK_ENV=production
SECRET_KEY=your-very-secure-secret-key-change-this
DATABASE_URL=sqlite:///company_tasks.db
CORS_ORIGINS=https://yourdomain.com
PORT=5005
DEBUG=False
```

### Frontend Environment

`.env.production` dosyasını düzenleyin:

```env
VITE_API_BASE_URL=https://your-api-domain.com/api
VITE_APP_ENV=production
```

## 🔍 Monitoring

### Health Check

```bash
curl http://localhost:5005/api/health
```

Başarılı response:
```json
{
  "status": "healthy",
  "timestamp": "2025-07-12T21:00:00.000Z",
  "version": "1.0.0"
}
```

### Logs

```bash
# Docker logs
docker-compose logs -f app

# Manuel deployment logs
tail -f backend/app.log
```

## 🌐 Cloud Deployment Seçenekleri

### 1. Heroku

```bash
# Heroku CLI ile
heroku create your-app-name
git push heroku main
```

### 2. Railway

```bash
# Railway CLI ile
railway login
railway init
railway up
```

### 3. DigitalOcean App Platform

1. GitHub repo'nuzu bağlayın
2. Build Command: `npm run build`
3. Run Command: `cd backend && gunicorn app:app`

### 4. AWS/Azure/GCP

Docker image'ını container registry'ye push edin ve container service'te çalıştırın.

## 📱 PWA Features

Deploy edilen uygulama şu PWA özelliklerini içerir:

- ✅ **Offline çalışma** (Service Worker ile)
- ✅ **Add to Home Screen** (iOS/Android)
- ✅ **Push notifications** hazır
- ✅ **Responsive design** (mobile-first)
- ✅ **App-like navigation** (SPA)

## 🔒 Güvenlik

Production'da mutlaka:

1. **SECRET_KEY** değiştirin
2. **DEBUG=False** yapın
3. **CORS_ORIGINS** doğru domain'e ayarlayın
4. **HTTPS** kullanın
5. **Database backup** stratejisi oluşturun

## 📊 Performance

Production optimizasyonları:

- ✅ Minified JS/CSS bundles
- ✅ Gzip compression
- ✅ Service Worker caching
- ✅ Database indexing
- ✅ Multi-worker Gunicorn setup

## 🛠️ Troubleshooting

### Common Issues

1. **Port çakışması**: `docker-compose.yml`'de port değiştirin
2. **CORS hatası**: CORS_ORIGINS environment variable'ını kontrol edin
3. **Database hatası**: Volume mount'ları kontrol edin
4. **Build hatası**: Node.js/npm versiyonlarını kontrol edin

### Debug Mode

Development mode'da çalıştırmak için:

```bash
# Backend debug
cd backend && ./start.sh

# Frontend dev server
npm run dev
```

## 📞 Support

Herhangi bir sorun durumunda:
- Logs'ları kontrol edin: `docker-compose logs`
- Health check yapın: `curl localhost:5005/api/health`
- Database backup'ınızı kontrol edin

---

**🎉 Deployment tamamlandıktan sonra http://localhost:5005 adresinden uygulamanıza erişebilirsiniz!**
