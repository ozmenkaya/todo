# OneSignal Production Migration Guide

## 🚨 Production Database Error Çözümü

Production'da şu hatayı alıyorsanız:
```
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedColumn) column user.push_notifications_enabled does not exist
```

Bu, PostgreSQL database'inde OneSignal notification sütunlarının eksik olduğunu gösterir.

## 🔧 Migration Yöntemleri

### Yöntem 1: Admin Panel Migration (Önerilen)

1. **Production site'a admin olarak giriş yap**
   - https://yourapp.digitalocean.com/login
   - Username: `admin`
   - Password: `[admin_password]`

2. **Yedekleme Yönetimi sayfasına git**
   - URL: `/admin/backups`
   - Veya Admin menüsünden "Yedekleme Yönetimi"

3. **OneSignal Migration butonuna tıkla**
   - Sarı "OneSignal Migration" butonu
   - Onay dialog'unda "OK" tıkla
   - Başarı mesajını bekle

### Yöntem 2: DigitalOcean Console'dan Direct Migration

1. **DigitalOcean Dashboard'a git**
   - Apps > Your Todo App
   - Console tab'ı

2. **Migration script'ini çalıştır**
   ```bash
   python production_onesignal_migration.py
   ```

3. **Uygulamayı restart et**
   ```bash
   # App Platform otomatik restart yapar, manuel gerekli değil
   ```

### Yöntem 3: Database Direct Access

1. **DigitalOcean Database Console'a erişim**
   - Database > Your PostgreSQL DB
   - Connect via Terminal

2. **Manuel SQL komutları**
   ```sql
   -- OneSignal sütunlarını ekle
   ALTER TABLE users ADD COLUMN push_notifications_enabled BOOLEAN DEFAULT true;
   ALTER TABLE users ADD COLUMN task_assignment_notifications BOOLEAN DEFAULT true;
   ALTER TABLE users ADD COLUMN task_completion_notifications BOOLEAN DEFAULT true;
   ALTER TABLE users ADD COLUMN reminder_notifications BOOLEAN DEFAULT true;
   ALTER TABLE users ADD COLUMN report_notifications BOOLEAN DEFAULT true;
   ALTER TABLE users ADD COLUMN onesignal_player_id VARCHAR(255);
   ```

## ✅ Migration Sonrası Kontrol

Migration başarılı olduktan sonra:

1. **Uygulama restart edilir** (App Platform otomatik)
2. **Login sayfası çalışır**
3. **OneSignal notifications aktif olur**
4. **Admin panelinde notification settings görünür**

## 🔍 Troubleshooting

### Migration Durumu Kontrolü
```sql
-- Sütunların var olup olmadığını kontrol et
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'users' 
AND column_name LIKE '%notification%' OR column_name = 'onesignal_player_id';
```

### Beklenen Sonuç (6 sütun):
- `push_notifications_enabled`
- `task_assignment_notifications` 
- `task_completion_notifications`
- `reminder_notifications`
- `report_notifications`
- `onesignal_player_id`

## 📱 OneSignal Test

Migration sonrası test etmek için:
1. Admin panelinde "Notification Settings"e git
2. Notification permissions'ları enable et
3. Test notification gönder
4. Browser/device'da notification alındığını kontrol et

---
*Son güncelleme: 13 Eylül 2025*