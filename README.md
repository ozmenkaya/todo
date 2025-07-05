# Helmex Todo Yönetim Sistemi

Modern, güvenli ve kullanıcı dostu bir şirket içi todo/görev yönetim sistemi. Python Flask ile geliştirilmiştir.

## 🎯 Özellikler

### 👥 Kullanıcı Rolleri
- **Admin**: Tüm sistemi yönetir, kullanıcı ekler/çıkarır, tüm görevleri görür
- **Manager**: Kendi departmanındaki görevleri yönetir, yeni görev oluşturur
- **Employee**: Sadece kendine atanan görevleri görür ve günceller

### 📋 Görev Yönetimi
- **Görev Oluşturma**: Başlık, açıklama, öncelik, bitiş tarihi
- **Durum Takibi**: Beklemede, Devam Ediyor, Tamamlandı, İptal Edildi
- **Öncelik Seviyeleri**: Düşük, Orta, Yüksek, Acil
- **Yorum Sistemi**: Görevlere yorum ekleme
- **Gelişmiş Atama**: Manager'lar diğer manager'lara ve çalışanlara atama yapabilir

### 🔔 Anımsatıcı Sistemi
- **Kişisel Anımsatıcılar**: Her kullanıcı kendi anımsatıcılarını oluşturabilir
- **Tarih ve Saat**: Özel tarih ve saat belirleme
- **Anlık Bildirimler**: Bugünün anımsatıcıları için otomatik bildirimler
- **Durum Takibi**: Tamamlanan/bekleyen anımsatıcı durumları
- **Filtreleme**: Tarih, durum ve arama filtreleri

### 📊 Raporlama ve İstatistikler
- **Genel İstatistikler**: Toplam, tamamlanan, bekleyen görevler
- **Departman Bazında Rapor**: Departman performansları
- **Görsel Grafikler**: Pasta grafikler ve progress barlar
- **Filtreleme**: Durum, öncelik ve arama filtreleri

### 🔒 Güvenlik
- **Kullanıcı Kimlik Doğrulama**: Güvenli giriş sistemi
- **Yetki Kontrolü**: Rol bazlı erişim kontrolü
- **Şifreli Saklama**: Güvenli şifre hash'leme

## 🚀 Kurulum

### Gereksinimler
- Python 3.8+
- pip

### Adım Adım Kurulum

1. **Projeyi İndirin**
```bash
git clone [repository-url]
cd todo
```

2. **Sanal Ortam Oluşturun**
```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# veya
.venv\Scripts\activate  # Windows
```

3. **Bağımlılıkları Yükleyin**
```bash
pip install -r requirements.txt
```

4. **Uygulamayı Başlatın**
```bash
python app.py
```

5. **Tarayıcıda Açın**
```
http://localhost:5003
```

6. **Demo Verilerini Yükleyin (İsteğe bağlı)**
```bash
python create_demo_data.py
```

## 👤 İlk Giriş

### Varsayılan Admin Hesabı
- **Kullanıcı Adı**: `admin`
- **Şifre**: `admin123`
- **Rol**: Admin

İlk girişten sonra admin panelinden yeni kullanıcılar ekleyebilirsiniz.

## 📱 Kullanım Kılavuzu

### Yeni Kullanıcı Ekleme (Admin)
1. Admin hesabıyla giriş yapın
2. Sağ üst köşedeki menüden "Kullanıcı Yönetimi"ne tıklayın
3. "Yeni Kullanıcı" butonuna tıklayın
4. Kullanıcı bilgilerini doldurun
5. Rol ve departman seçin

### Görev Oluşturma (Admin/Manager)
1. Ana sayfada "Yeni Görev" butonuna tıklayın
2. Görev başlığı ve açıklamasını yazın
3. Atanacak kişiyi seçin
4. Öncelik ve bitiş tarihini belirleyin
5. "Görevi Oluştur" butonuna tıklayın

### Anımsatıcı Ekleme
1. Sağ üst köşedeki menüden "Yeni Anımsatıcı"ya tıklayın
2. Başlık ve açıklama yazın
3. Tarih ve saat seçin
4. Hızlı seçenekleri kullanabilirsiniz (bugün, yarın, vb.)
5. "Anımsatıcı Oluştur" butonuna tıklayın

### Anımsatıcı Yönetimi
1. "Anımsatıcılarım" sayfasında tüm anımsatıcılarınızı görün
2. Tamamlanan anımsatıcıları işaretleyebilirsiniz
3. Filtreleme seçenekleriyle istediğiniz anımsatıcıları bulun
4. Ana sayfada bugünün anımsatıcıları otomatik gösterilir

### Atadığım Görevleri Takip Etme
1. Ana sayfada "Atadıklarım" sekmesine tıklayın
2. Atadığınız görevlerin durumlarını görün
3. Tamamlanma oranlarını takip edin
4. Gerekirse görev detaylarına gidip yorum ekleyin

### Görev Sekmesi Yapısı
- **Bana Atananlar**: Size atanan görevler
- **Atadıklarım**: Başkalarına atadığınız görevler (varsa)
- **Departman Görevleri**: Manager'lar için departman görevleri
- **Tüm Görevler**: Admin için sistem geneli

## 🏗️ Teknik Detaylar

### Teknoloji Stack
- **Backend**: Python Flask
- **Veritabanı**: SQLite (SQLAlchemy ORM)
- **Frontend**: Bootstrap 5, HTML, CSS, JavaScript
- **Kimlik Doğrulama**: Flask-Login
- **Grafik**: Chart.js

### Veritabanı Yapısı
- **Users**: Kullanıcı bilgileri ve rolleri
- **Tasks**: Görev bilgileri ve durumları
- **Comments**: Görev yorumları
- **Reminders**: Kişisel anımsatıcılar

### Dosya Yapısı
```
todo/
├── app.py              # Ana uygulama dosyası
├── requirements.txt    # Python bağımlılıkları
├── todo_company.db    # SQLite veritabanı
└── templates/         # HTML şablonları
    ├── base.html
    ├── index.html
    ├── login.html
    ├── create_task.html
    ├── task_detail.html
    ├── users.html
    ├── add_user.html
    ├── reminders.html     # YENİ: Anımsatıcı listesi
    ├── add_reminder.html  # YENİ: Anımsatıcı ekleme
    └── stats.html
```

## 🎨 Özelleştirme

### Yeni Departman Ekleme
Kullanıcı oluştururken departman alanına yeni departman adı yazabilirsiniz.

### Rol İzinleri
`app.py` dosyasındaki yetki kontrollerini düzenleyerek rollerin yetkilerini değiştirebilirsiniz.

### Görsel Tasarım
Bootstrap CSS sınıflarını ve özel CSS'leri değiştirerek görünümü özelleştirebilirsiniz.

## 🔧 Sorun Giderme

### Port Problemi
Eğer 5003 portu kullanımda ise, `app.py` dosyasının en altındaki port numarasını değiştirin:
```python
app.run(debug=True, host='0.0.0.0', port=5004)
```

### Veritabanı Sıfırlama
```bash
rm todo_company.db
python app.py  # Yeni veritabanı oluşturulacak
```

### Admin Şifre Sıfırlama
`app.py` dosyasındaki `create_admin_user()` fonksiyonunu düzenleyin.

## 📈 Gelecek Geliştirmeler

- [x] Kişisel anımsatıcı sistemi ✅
- [x] Manager'ların birbirlerine görev atayabilmesi ✅
- [x] Atadığı görevleri takip etme sistemi ✅
- [ ] E-posta bildirimleri
- [ ] Dosya ekleme özelliği
- [ ] Gantt şemaları
- [ ] API endpoints
- [ ] Mobil uygulama
- [ ] LDAP entegrasyonu
- [ ] Gelişmiş raporlama
- [ ] Tekrarlayan anımsatıcılar
- [ ] Ekip takvimi entegrasyonu

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Commit yapın (`git commit -m 'Add some AmazingFeature'`)
4. Push yapın (`git push origin feature/AmazingFeature`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 📞 İletişim

Sorularınız için: [your-email@company.com]

---

**Not**: Bu uygulama geliştirme amaçlı olup, production ortamında kullanmadan önce ek güvenlik önlemleri alınmalıdır.
