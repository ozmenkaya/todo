#!/bin/bash

# DigitalOcean Droplet Deploy Script
echo "🌊 Deploying to DigitalOcean Droplet"
echo "==================================="

# Variables - Bu değerleri kendi setup'ınıza göre değiştirin
DROPLET_IP="your-droplet-ip"
DROPLET_USER="root"  # veya sudo yetkili kullanıcı
APP_DIR="/var/www/task-management"
DOMAIN="your-domain.com"  # isteğe bağlı

echo "📤 Uploading files to droplet..."

# Rsync ile dosyaları yükle
rsync -avz --exclude node_modules --exclude .git --exclude dist . $DROPLET_USER@$DROPLET_IP:$APP_DIR/

echo "🔧 Setting up on droplet..."

# Droplet'te komutları çalıştır
ssh $DROPLET_USER@$DROPLET_IP << EOF
cd $APP_DIR

echo "📦 Installing dependencies..."
# Frontend dependencies
npm install
npm run build

# Backend dependencies
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "🗄️ Setting up database..."
python3 -c "from app import init_db; init_db()"

echo "🌐 Setting up Nginx..."
# Nginx config
cat > /etc/nginx/sites-available/task-management << 'NGINX_EOF'
server {
    listen 80;
    server_name $DOMAIN;
    
    # Frontend
    location / {
        root $APP_DIR/dist;
        try_files \$uri \$uri/ /index.html;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:5005;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
NGINX_EOF

# Enable site
ln -sf /etc/nginx/sites-available/task-management /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

echo "🚀 Starting backend service..."
# Systemd service
cat > /etc/systemd/system/task-management.service << 'SERVICE_EOF'
[Unit]
Description=Company Task Management Backend
After=network.target

[Service]
Type=exec
User=www-data
WorkingDirectory=$APP_DIR/backend
Environment=PATH=$APP_DIR/backend/venv/bin
ExecStart=$APP_DIR/backend/venv/bin/gunicorn --bind 127.0.0.1:5005 --workers 2 app:app
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE_EOF

systemctl daemon-reload
systemctl enable task-management
systemctl start task-management

echo "✅ Deployment completed!"
echo "🌐 Your app should be available at: http://$DOMAIN"
echo "📊 Check status: systemctl status task-management"
EOF

echo "🎉 Deploy completed! Check your droplet."
