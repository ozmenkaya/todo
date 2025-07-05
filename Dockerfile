FROM python:3.11-slim

WORKDIR /app

# Sistem paketlerini yükle
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python gereksinimlerini kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyala
COPY . .

# Non-root user oluştur
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Port'u belirt
EXPOSE 5004

# Health check ekle
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5004/ || exit 1

# Uygulamayı başlat
CMD ["python", "app.py"]
