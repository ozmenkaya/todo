#!/bin/bash

# 🐳 Docker Deployment Script for Todo App with OneSignal
echo "🐳 Docker deployment başlıyor..."

# Build Docker image
echo "📦 Docker image build ediliyor..."
docker build -t todo-app-onesignal .

# Run with environment variables
echo "🚀 Container başlatılıyor..."
docker run -d \
  --name todo-app \
  -p 8080:8080 \
  -e ONESIGNAL_APP_ID="0047e2bf-7209-4b1c-b222-310e700a9780" \
  -e ONESIGNAL_API_KEY="os_v2_app_abd6fp3sbffrzmrcgehhacuxqcalxza3656u4p5gzxpcmji55xmckrxansybtyo6nvii2pq2onkoguolsra7lj6j3thkrq5sijnesvy" \
  -e ONESIGNAL_APNS_TEAM_ID="435XR8VR9X" \
  -e ONESIGNAL_APNS_BUNDLE_ID="com.helmex" \
  -e FLASK_ENV="production" \
  -e SECRET_KEY="$(openssl rand -hex 32)" \
  -v $(pwd)/instance:/app/instance \
  todo-app-onesignal

echo "✅ Container başlatıldı!"
echo "🌐 Uygulama: http://localhost:8080"
echo "📱 OneSignal push notifications aktif!"

# Show container status
docker ps | grep todo-app