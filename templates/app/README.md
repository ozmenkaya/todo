# 📱 Şirket Görev Yöneticisi - Mobil PWA

Modern bir şirket içi görev ve rapor yönetim sistemi için Progressive Web Application (PWA).

## 🚀 Özellikler

- **📱 Mobil-Öncelikli Tasarım**: iOS ve Android için optimize edilmiş responsive tasarım
- **🔄 Progressive Web App**: Mobil cihazlarda yüklenebilir uygulama
- **🔐 Güvenli Kimlik Doğrulama**: Flask backend ile session-based authentication
- **📋 Görev Yönetimi**: Görev oluşturma, güncelleme, takibi
- **📄 Rapor Sistemi**: Şirket raporları paylaşımı ve yönetimi
- **🔔 Bildirimler**: Real-time push notifications
- **📱 Offline Çalışma**: Service Worker ile offline destek
- **🎨 Modern UI**: Material-UI ile modern, kullanıcı dostu arayüz

## 🛠️ Teknoloji Stack'i

- **Frontend**: React 18 + TypeScript
- **Build Tool**: Vite
- **UI Framework**: Material-UI (MUI)
- **State Management**: React Context API
- **Routing**: React Router
- **HTTP Client**: Axios
- **PWA**: Vite PWA Plugin + Workbox
- **Backend API**: Flask (http://localhost:5004)

## 📦 Kurulum

1. **Dependencies yükle:**
```bash
npm install
```

2. **Development server başlat:**
```bash
npm run dev
```

3. **Backend'i çalıştır:**
   - Flask uygulamasının `http://localhost:5004` adresinde çalıştığından emin ol

4. **Uygulamayı aç:**
   - Tarayıcıda `http://localhost:3000` adresine git

## 🚀 Production Build

```bash
npm run build
npm run preview
```

## 📱 PWA Kurulumu

1. **Desktop'ta**: Tarayıcının adres çubuğundaki "Install" butonuna tıkla
2. **Mobil'de**: Tarayıcı menüsünden "Add to Home Screen" seç

## 🔧 API Konfigürasyonu

Uygulama, mevcut Flask backend'e bağlanır:
- **Base URL**: `http://localhost:5004`
- **CORS**: Cross-origin requests desteklenir
- **Session**: Cookie-based authentication

## 📁 Proje Yapısı

```
src/
├── components/          # Reusable UI components
├── contexts/           # React Context providers
├── pages/              # Page components
├── services/           # API service layer
├── types/              # TypeScript type definitions
└── App.tsx             # Main application component
```

## 🔐 Demo Hesaplar

- **Admin**: username: `admin`, password: `admin123`
- **User**: username: `user`, password: `user123`

## 🌟 Gelecek Özellikler

- [ ] Push notifications
- [ ] Offline data sync
- [ ] Dark mode
- [ ] Multi-language support
- [ ] File attachments
- [ ] Advanced reporting
- [ ] Team collaboration tools
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```
