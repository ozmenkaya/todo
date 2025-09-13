# OneSignal Push Notification Integration

Bu dosya, todo uygulamasına entegre edilen OneSignal push notification sisteminin tüm detaylarını içerir.

## 🚀 Genel Bakış

OneSignal entegrasyonu başarıyla tamamlanmış ve aşağıdaki platformları desteklemektedir:
- ✅ **Web Browsers** (Chrome, Firefox, Safari, Edge)
- ✅ **iOS** (APNs ile)
- ✅ **Android** (FCM ile)

## 🔧 Konfigürasyon

### OneSignal Temel Ayarları
- **App ID**: `0047e2bf-7209-4b1c-b222-310e700a9780`
- **REST API Key**: Güvenli şekilde yapılandırılmış
- **Web Push**: Aktif

### iOS APNs Konfigürasyonu
- **Team ID**: `435XR8VR9X`
- **Bundle ID**: `com.helmex`
- **Authentication Type**: `.p8 Auth Key`

## 📁 Dosya Yapısı

```
todo/
├── onesignal_config.py           # OneSignal konfigürasyon sınıfı
├── onesignal_service.py          # Bildirim gönderme servisi
├── templates/
│   ├── base.html                 # OneSignal SDK entegrasyonu
│   └── notification_settings.html # Kullanıcı bildirim ayarları
└── models.py                     # User modelinde bildirim tercihleri
```

## 🔔 Bildirim Türleri

### 1. Görev Bildirimleri
- **Görev Atama**: Yeni görev atandığında
- **Görev Tamamlama**: Görev tamamlandığında oluşturana bildirim

### 2. Hatırlatıcı Bildirimleri
- **Zamanı Gelen Hatırlatıcılar**: Belirlenen tarih/saatte

### 3. Rapor Bildirimleri
- **Yeni Rapor**: Rapor oluşturulduğunda
- **Rapor Paylaşımı**: Rapor paylaşıldığında

## 🎛️ Kullanıcı Tercihleri

Her kullanıcı aşağıdaki bildirim türlerini ayrı ayrı açıp kapatabilir:

```sql
-- User tablosundaki yeni kolonlar
push_notifications_enabled          BOOLEAN DEFAULT TRUE
task_assignment_notifications       BOOLEAN DEFAULT TRUE  
task_completion_notifications       BOOLEAN DEFAULT TRUE
reminder_notifications              BOOLEAN DEFAULT TRUE
report_notifications                BOOLEAN DEFAULT TRUE
onesignal_player_id                VARCHAR(255)
```

## 🌐 Frontend Entegrasyonu

### OneSignal SDK v16
```html
<!-- base.html içinde -->
<script src="https://cdn.onesignal.com/sdks/web/v16/OneSignalSDK.page.js" defer></script>
```

### Otomatik Konfigürasyon
- Sayfa yüklendiğinde OneSignal otomatik başlatılır
- Kullanıcı izni otomatik istenir
- Player ID otomatik kaydedilir

### Service Worker
- OneSignal service worker'ı otomatik yüklenir
- Background notification desteği

## 🔄 Backend Entegrasyonu

### Bildirim Gönderme Fonksiyonları

```python
# Görev bildirimi
send_task_notification(
    task_title="Yeni Görev",
    message="Size yeni bir görev atandı",
    user_ids=[1, 2, 3],
    task_id=123
)

# Hatırlatıcı bildirimi  
send_reminder_notification(
    reminder_title="Toplantı Hatırlatıcısı",
    message="15 dakika sonra toplantınız var",
    user_ids=[1],
    reminder_id=456
)
```

### Kullanıcı Filtreleme
Tüm bildirim fonksiyonları kullanıcı tercihlerini otomatik kontrol eder:
- Push notifications devre dışı ise bildirim gönderilmez
- İlgili bildirim türü kapalı ise atlanır

## 📱 Kullanıcı Arayüzü

### Bildirim Ayarları Sayfası
- **URL**: `/notification_settings`
- **Erişim**: Kullanıcı dropdown menüsü → "Bildirim Ayarları"
- **Özellikler**: 
  - OneSignal durumu kontrolü
  - İzin talep butonu
  - Bildirim türleri toggle'ları
  - Responsive tasarım

## 🔒 Güvenlik

### API Key Güvenliği
- REST API Key environment variable'da saklanır
- Fallback değerler production için uygun
- Client-side'da API key expose edilmez

### Kullanıcı Yetkilendirme  
- Sadece login olan kullanıcılar bildirim alır
- Her kullanıcı kendi tercihlerini kontrol eder
- Admin yetkisi gerektiren işlemler ayrılmış

## 🧪 Test Edilmiş Özellikler

### ✅ Tamamlanan Testler
- OneSignal API bağlantısı (Status: 200)
- Bildirim gönderimi (Test ID: 85c21e78-810b-4adf-8306-a814813c1e31)
- Database migration (6 kolon eklendi)  
- Flask app başlatma (Port: 5004)
- User authentication flow
- Template rendering

### 🔄 Sürekli Test Edilmesi Gerekenler
- Farklı tarayıcılarda push notification
- iOS device test (APNs)
- Android device test (FCM)
- Notification permission handling
- Service worker functionality

## 🚀 Deployment

### Production Ortamı İçin
```bash
# Environment variables
export ONESIGNAL_APP_ID="0047e2bf-7209-4b1c-b222-310e700a9780"
export ONESIGNAL_API_KEY="os_v2_app_abd6fp3sbffrzmrcgehhacuxqc..."
export ONESIGNAL_APNS_TEAM_ID="435XR8VR9X"
export ONESIGNAL_APNS_BUNDLE_ID="com.helmex"
```

### Database Migration
Database migration otomatik olarak `app.py` başlatılırken çalışır.

## 📈 Monitoring & Analytics

### OneSignal Dashboard
- Bildirim istatistikleri
- Delivery rates
- Click-through rates
- User engagement metrics

### Flask Logging
```python
# OneSignal işlemleri loglanır
logger.info("Notification sent successfully")
logger.error("OneSignal API error")
```

## 🔧 Troubleshooting

### Yaygın Sorunlar

1. **403 API Error**
   - REST API Key kontrolü
   - Authorization header formatı

2. **Bildirim Gelmiyorsa**  
   - Browser notification permission
   - OneSignal player ID kaydı
   - User notification preferences

3. **Service Worker Issues**
   - HTTPS gerekliliği (production)
   - Service worker path kontrolü

### Debug Komutları
```javascript
// Console'da OneSignal durumu
OneSignal.User.onesignalId
OneSignal.Notifications.permission

// Python'da test
python -c "from onesignal_service import send_task_notification; print('OK')"
```

## 📞 Destek

Bu OneSignal entegrasyonu için:
- OneSignal Documentation: https://documentation.onesignal.com/
- APNs Setup Guide: https://documentation.onesignal.com/docs/ios-sdk-setup
- Web Push Guide: https://documentation.onesignal.com/docs/web-push-quickstart

---
**Son Güncelleme**: 13 Eylül 2025  
**Durum**: ✅ Aktif ve Çalışıyor  
**Test ID**: 85c21e78-810b-4adf-8306-a814813c1e31