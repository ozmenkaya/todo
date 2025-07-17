# 🏢 Şirket Görev Yöneticisi - Tam Stack PWA

Modern bir şirket içi görev ve rapor yönetim sistemi. Bu proje, **Flask backend** ve **React PWA frontend** içeren tam stack bir mobil uygulamadır.

## 🚀 Özellikler

### 📱 Frontend (PWA)
- **Progressive Web App**: Mobil cihazlarda yüklenebilir
- **React + TypeScript**: Modern ve tip güvenli geliştirme
- **Material-UI**: Profesyonel ve modern arayüz
- **Offline Çalışma**: Service Worker ile offline destek
- **Responsive Tasarım**: Mobil-öncelikli responsive tasarım
- **Real-time Bildirimler**: Push notifications desteği

### 🔧 Backend (Flask API)
- **RESTful API**: Modern API tasarımı
- **SQLAlchemy ORM**: Veritabanı yönetimi
- **Session Authentication**: Güvenli kimlik doğrulama
- **CORS Desteği**: Cross-origin requests
- **SQLite Database**: Kolay kurulum için SQLite

### 📋 İş Özellikleri
- **👤 Kullanıcı Yönetimi**: Admin, yönetici ve çalışan rolleri
- **📝 Görev Yönetimi**: CRUD operasyonları, atama, durum takibi
- **📄 Rapor Sistemi**: Rapor oluşturma ve paylaşma
- **⏰ Hatırlatmalar**: Zaman bazlı hatırlatma sistemi
- **📊 Dashboard**: Özet bilgiler ve istatistikler

## 🛠️ Teknoloji Stack'i

### Frontend
- **React 18** + **TypeScript**
- **Vite** (Build tool)
- **Material-UI (MUI)** 
- **React Router** (Navigation)
- **Axios** (HTTP Client)
- **Workbox** (Service Worker)

### Backend  
- **Flask 3.0** + **Python**
- **Flask-SQLAlchemy** (ORM)
- **Flask-CORS** (CORS support)
- **SQLite** (Database)
- **Werkzeug** (Security)

## 📦 Kurulum ve Çalıştırma

### 🔥 Hızlı Başlangıç

1. **Repository'yi klonlayın:**
```bash
cd /Users/ozmenkaya/todo/templates/app
```

2. **Backend'i başlatın:**
```bash
cd backend
chmod +x start.sh
./start.sh
```

3. **Yeni terminal açıp Frontend'i başlatın:**
```bash
npm install
npm run dev
```

4. **Uygulamayı açın:**
   - Frontend: http://localhost:3004
   - Backend API: http://localhost:5005

### 🔑 Demo Hesaplar
- **Admin**: `admin` / `admin123`
- **User**: `user` / `user123`

## 📁 Proje Yapısı

```
templates/app/
├── backend/                 # Flask Backend
│   ├── app.py              # Ana Flask uygulaması
│   ├── requirements.txt    # Python bağımlılıkları
│   ├── start.sh           # Backend başlatma scripti
│   └── company_tasks.db   # SQLite veritabanı (otomatik oluşur)
├── src/                    # React Frontend
│   ├── components/         # UI bileşenleri
│   ├── contexts/          # React Context providers
│   ├── pages/             # Sayfa bileşenleri
│   ├── services/          # API servis katmanı
│   └── types/             # TypeScript tip tanımları
├── public/                # PWA statik dosyaları
├── package.json           # Frontend bağımlılıkları
├── vite.config.ts         # Vite konfigürasyonu
└── README.md             # Bu dosya
```

## 🔧 Detaylı Kurulum

### Backend Kurulumu

1. **Python sanal ortamı oluşturun:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate     # Windows
```

2. **Bağımlılıkları yükleyin:**
```bash
pip install -r requirements.txt
```

3. **Flask uygulamasını başlatın:**
```bash
python app.py
```

Backend şu adreste çalışacak: http://localhost:5005

### Frontend Kurulumu

1. **Node.js bağımlılıklarını yükleyin:**
```bash
npm install
```

2. **Development server'ı başlatın:**
```bash
npm run dev
```

3. **Production build için:**
```bash
npm run build
npm run preview
```

Frontend şu adreste çalışacak: http://localhost:3004

## 🌐 API Endpoints

### Authentication
- `POST /login` - Kullanıcı girişi
- `POST /logout` - Kullanıcı çıkışı
- `GET /api/current_user` - Mevcut kullanıcı bilgileri

### Tasks
- `GET /api/tasks` - Görevleri listele
- `POST /api/tasks` - Yeni görev oluştur
- `GET /api/tasks/{id}` - Görev detayı
- `PUT /api/tasks/{id}` - Görev güncelle
- `DELETE /api/tasks/{id}` - Görev sil

### Reports
- `GET /api/reports` - Raporları listele
- `POST /api/reports` - Yeni rapor oluştur
- `GET /api/reports/{id}` - Rapor detayı

### Reminders
- `GET /api/reminders` - Hatırlatmaları listele
- `GET /api/today_reminders` - Bugünün hatırlatmaları
- `POST /api/reminders` - Yeni hatırlatma oluştur

### Users & Notifications
- `GET /api/users` - Kullanıcıları listele
- `GET /api/notification_counts` - Bildirim sayıları

## 📱 PWA Özellikleri

### Kurulum
- **Desktop**: Tarayıcıdaki "Install" butonuna tıklayın
- **Mobil**: Tarayıcı menüsünden "Add to Home Screen" seçin

### Offline Çalışma
- Service Worker ile temel sayfa caching
- API istekleri için NetworkFirst stratejisi
- Backend çalışmazsa otomatik Mock API fallback

### Bildirimler
- Browser push notifications desteği
- Real-time görev ve hatırlatma bildirimleri

## 🔄 Fallback Sistemi

Uygulama, backend çalışmadığında otomatik olarak Mock API'ye geçer:
- Backend bağlantı hatası durumunda mock data kullanır
- Development sırasında backend başlatmadan test edilebilir
- Offline demo için idealdir

## 🛡️ Güvenlik

- Session-based authentication
- CORS güvenlik yapılandırması
- SQL injection koruması (SQLAlchemy ORM)
- XSS koruması (Flask built-in)

## 🚀 Production Deployment

### Backend Production
```bash
# Gunicorn ile production server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5004 app:app
```

### Frontend Production
```bash
# Production build
npm run build
# Static files serve
npm run preview
```

### Environment Variables
```bash
# Backend (.env)
FLASK_ENV=production
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://...

# Frontend (.env)
VITE_API_BASE_URL=https://your-api-domain.com
```

## 📊 Database Schema

### Users
- id, username, email, password_hash
- first_name, last_name, role, department
- created_at

### Tasks
- id, title, description, status, priority
- created_by, due_date, created_at, updated_at
- Many-to-many: assignees

### Reports
- id, title, content, created_by
- created_at, updated_at
- Many-to-many: shared_users

### Reminders
- id, title, description, reminder_time
- user_id, created_at, is_completed

## 🔧 Geliştirme

### Frontend Development
```bash
# Linting
npm run lint

# Type checking
npx tsc --noEmit

# Development server with hot reload
npm run dev
```

### Backend Development
```bash
# Debug mode
export FLASK_DEBUG=1
python app.py

# Database migration (when using migrations)
flask db init
flask db migrate
flask db upgrade
```

## 🐛 Troubleshooting

### Backend bağlantı sorunları
- Flask server'ın 5004 portunda çalıştığından emin olun
- CORS ayarlarını kontrol edin
- Firewall/port bloğu olup olmadığına bakın

### Frontend build sorunları  
- `node_modules` klasörünü silin ve `npm install` çalıştırın
- TypeScript type errors'ını kontrol edin
- Vite config dosyasını kontrol edin

### PWA kurulum sorunları
- HTTPS gereksinimi (production'da)
- Service Worker registrasyonu
- Manifest.json dosyası kontrolü

## 📝 TODO / Gelecek Özellikler

- [ ] **Real-time updates** (WebSocket/Socket.IO)
- [ ] **File attachments** (görev ve raporlara dosya ekleme)
- [ ] **Email notifications** (e-posta bildirimleri)
- [ ] **Advanced reporting** (grafik ve analitik)
- [ ] **Team collaboration** (takım özellikleri)
- [ ] **Dark mode** (karanlık tema)
- [ ] **Multi-language** (çoklu dil desteği)
- [ ] **Mobile app** (React Native/Ionic)
- [ ] **Desktop app** (Electron)
- [ ] **Advanced PWA** (background sync, advanced caching)

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 👥 İletişim

Proje hakkında sorularınız için:
- GitHub Issues kullanabilirsiniz
- E-posta ile iletişime geçebilirsiniz

---

🎉 **Uygulama başarıyla çalışıyor! Backend: http://localhost:5005 | Frontend: http://localhost:3004**
