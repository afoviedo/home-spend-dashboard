#!/bin/bash

# Script de deployment simple (sin Docker)
echo "🚀 Deployment simple del Dashboard de Gastos del Hogar..."

# Variables
DOMAIN="tu-dominio.com"
APP_DIR="/opt/home-spend-dashboard"
SERVICE_NAME="home-spend-dashboard"

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo_success() { echo -e "${GREEN}✅ $1${NC}"; }
echo_warning() { echo -e "${YELLOW}⚠️ $1${NC}"; }
echo_error() { echo -e "${RED}❌ $1${NC}"; }

# 1. Instalar dependencias del sistema
echo "📦 Instalando dependencias..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git

# 2. Crear directorio de aplicación
echo "📁 Creando directorio de aplicación..."
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# 3. Copiar archivos de aplicación
echo "📋 Copiando archivos..."
cp dashboard_simple.py $APP_DIR/
cp onedrive_graph.py $APP_DIR/
cp requirements.txt $APP_DIR/
cp -r .streamlit $APP_DIR/
cp .env $APP_DIR/

# 4. Configurar entorno virtual
echo "🐍 Configurando entorno virtual..."
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Crear servicio systemd
echo "⚙️ Creando servicio systemd..."
sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null <<EOF
[Unit]
Description=Home Spend Dashboard
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/streamlit run dashboard_simple.py --server.port=8501 --server.address=127.0.0.1
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 6. Configurar Nginx
echo "🌐 Configurando Nginx..."
sudo tee /etc/nginx/sites-available/$DOMAIN > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN;
    
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

# Habilitar sitio
sudo ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# 7. Configurar SSL
echo "🔒 Configurando SSL..."
sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email tu-email@ejemplo.com

# 8. Iniciar servicios
echo "🚀 Iniciando servicios..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

# 9. Configurar firewall
echo "🔥 Configurando firewall..."
sudo ufw allow 'Nginx Full'
sudo ufw allow ssh
sudo ufw --force enable

echo_success "¡Deployment completado!"
echo "🌐 Tu dashboard está disponible en: https://$DOMAIN"
echo ""
echo "📋 Comandos útiles:"
echo "  sudo systemctl status $SERVICE_NAME     # Ver estado"
echo "  sudo systemctl restart $SERVICE_NAME    # Reiniciar"
echo "  sudo journalctl -u $SERVICE_NAME -f     # Ver logs"
