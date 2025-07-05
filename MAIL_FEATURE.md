# 📧 Acil Görev Mail Bildirimi Özelliği

## ✅ Özellik Eklendi: Acil Görev Mail Bildirimi

### 🚨 Nasıl Çalışır:

1. **Yeni Görev Oluşturma** sayfasında öncelik olarak **"Acil"** seçildiğinde
2. Görev başarıyla oluşturulduktan sonra
3. **Atanan tüm kullanıcılara otomatik mail gönderilir**

### 📧 Mail İçeriği:

- **Konu:** 🚨 ACİL GÖREV: [Görev Başlığı]
- **İçerik:** 
  - Görev başlığı ve açıklaması
  - Atayan kişi bilgisi
  - Son tarih (varsa)
  - Oluşturulma tarihi
  - Özel acil görev tasarımı

### ⚙️ Konfigürasyon:

#### Production (DigitalOcean) için:

`.do/app.yaml` dosyasında mail ayarlarını yapılandırın:

```yaml
envs:
  # Gmail SMTP için örnek:
  - key: MAIL_SERVER
    value: smtp.gmail.com
  - key: MAIL_PORT
    value: "587"
  - key: MAIL_USE_TLS
    value: "true"
  - key: MAIL_USERNAME
    value: your-email@gmail.com
  - key: MAIL_PASSWORD
    value: your-app-password
  - key: MAIL_DEFAULT_SENDER
    value: noreply@helmex.com
```

#### Gmail için App Password:

1. Gmail hesabınızda 2FA aktif olmalı
2. Google Account Settings → Security → 2-Step Verification
3. App passwords → Generate new password
4. Bu password'ü `MAIL_PASSWORD` olarak kullanın

#### Diğer Mail Providers:

**Outlook/Hotmail:**
```yaml
- key: MAIL_SERVER
  value: smtp-mail.outlook.com
- key: MAIL_PORT
  value: "587"
```

**Yahoo:**
```yaml
- key: MAIL_SERVER
  value: smtp.mail.yahoo.com
- key: MAIL_PORT
  value: "587"
```

### 🧪 Test:

#### Development Ortamında:
- Mail konfigürasyonu yoksa otomatik olarak **simüle edilir**
- Console'da mail detayları görüntülenir
- Gerçek mail gönderilmez

#### Production Ortamında:
- Mail konfigürasyonu varsa **gerçek mail gönderilir**
- Mail konfigürasyonu yoksa **simüle edilir**

### 🎯 Kullanım Senaryosu:

1. **Manager/Admin** yeni görev oluşturur
2. **Öncelik: Acil** seçer
3. **Kullanıcıları seçer** (çoklu seçim mümkün)
4. **Görev oluştur** butonuna tıklar
5. ✅ **Otomatik mail gönderilir**: "🚨 Acil görev oluşturuldu ve X kişiye mail gönderildi!"

### 📊 Özellik Detayları:

- ✅ **Çoklu atama:** Birden fazla kişiye atanan acil görevlerde hepsine mail gider
- ✅ **HTML Email:** Güzel tasarımda, responsive mail şablonu
- ✅ **Error handling:** Mail gönderilemezse kullanıcı bilgilendirilir
- ✅ **Conditional:** Sadece "acil" öncelikli görevlerde çalışır
- ✅ **Email validation:** Email adresi olan kullanıcılara gönderilir

### 🔒 Güvenlik:

- Mail şifreleri environment variables'da saklanır
- App passwords kullanılarak güvenli bağlantı
- TLS encryption ile şifreli mail gönderimi

---

**🎊 Artık acil görevleriniz otomatik olarak ilgili kişilere mail ile bildirilecek!**
