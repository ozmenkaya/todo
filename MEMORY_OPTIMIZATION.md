# Memory Optimization for 512MB RAM

## 🧠 RAM Optimizasyonları

### 1. Database Connection Pool
- Worker sayısı: 2 → 1
- Pool size: 5 → 3
- Connection timeout: 20s → 10s
- Pool recycle: 300s → 180s

### 2. Gunicorn Configuration
- Workers: 2 → 1
- Connections: 1000 → 500
- Max requests: 1000 → 500
- Worker memory limit: 400MB

### 3. Query Optimization
- Her kategoride maksimum 50 görev yükleniyor
- Pagination ile büyük veri setleri sınırlandırıldı
- Department user'ları cache'leniyor

### 4. Memory Management
- Her request sonrası session cleanup
- 10 request'te bir garbage collection
- Database session'ların otomatik temizlenmesi

### 5. Notification API Optimization
- 3 ayrı query yerine 1 query + in-memory filtering
- assigned_to field hatası düzeltildi
- Error handling eklendi

### 6. Caching
- User'lar için LRU cache (maxsize=32)
- Department user'ları için cache (maxsize=16)
- Sık kullanılan veriler cache'leniyor

### 7. Memory Monitoring
- psutil ile memory usage tracking
- Başlangıç ve runtime memory monitoring
- Memory leak detection

## 📊 Beklenen Sonuçlar
- Memory kullanımı: ~400MB (%78 → %60)
- Response time: 20-30% iyileşme
- Database load: 50% azalma
- Worker restart frequency: Azalma

## 🔧 Monitoring
```bash
# Memory kullanımını kontrol et
ps aux | grep gunicorn
htop -p $(pgrep -f gunicorn)
```

## ⚠️ Notlar
- Eğer hala RAM problemi devam ederse 1GB'a upgrade önerilir
- Büyük data export'ları için ayrı worker kullanılabilir
- Cache TTL ayarları gerekirse eklenebilir
