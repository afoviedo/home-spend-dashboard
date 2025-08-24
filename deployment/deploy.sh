#!/bin/bash

# Script de deployment para VPS
echo "🚀 Iniciando deployment del Dashboard de Gastos del Hogar..."

# Variables de configuración
APP_NAME="home-spend-dashboard"
DOMAIN="tu-dominio.com"  # Cambia por tu dominio
EMAIL="tu-email@ejemplo.com"  # Para certificados SSL

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

echo_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

echo_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Función para verificar si un comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 1. Verificar dependencias
echo "🔍 Verificando dependencias..."

if ! command_exists docker; then
    echo_error "Docker no está instalado. Instalando Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo_success "Docker instalado"
fi

if ! command_exists docker-compose; then
    echo_error "Docker Compose no está instalado. Instalando..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo_success "Docker Compose instalado"
fi

# 2. Configurar firewall
echo "🔥 Configurando firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
echo_success "Firewall configurado"

# 3. Configurar certificados SSL con Let's Encrypt
echo "🔒 Configurando certificados SSL..."
if ! command_exists certbot; then
    sudo apt update
    sudo apt install -y certbot
fi

# Obtener certificados
sudo certbot certonly --standalone -d $DOMAIN --email $EMAIL --agree-tos --non-interactive

# Copiar certificados a la ubicación de nginx
sudo mkdir -p ./nginx/ssl
sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem ./nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem ./nginx/ssl/key.pem
sudo chown $USER:$USER ./nginx/ssl/*
echo_success "Certificados SSL configurados"

# 4. Configurar variables de entorno para producción
echo "⚙️ Configurando variables de entorno..."
if [ ! -f .env ]; then
    echo_warning "Archivo .env no encontrado. Creando plantilla..."
    cat > .env << EOF
# Configuración de Microsoft Graph API
CLIENT_ID=tu_client_id_aquí
CLIENT_SECRET=tu_client_secret_aquí
TENANT_ID=tu_tenant_id_aquí
REDIRECT_URI=https://$DOMAIN/callback

# Configuración de la aplicación
ENVIRONMENT=production
DEBUG=false
EOF
    echo_error "⚠️ IMPORTANTE: Edita el archivo .env con tus credenciales reales"
    exit 1
fi

# 5. Actualizar configuración de nginx con el dominio
sed -i "s/tu-dominio.com/$DOMAIN/g" ./nginx/nginx.conf
echo_success "Configuración de nginx actualizada"

# 6. Construir y ejecutar contenedores
echo "🐳 Construyendo y ejecutando contenedores..."
docker-compose down 2>/dev/null || true
docker-compose build
docker-compose up -d

# 7. Verificar que los servicios estén funcionando
echo "🔍 Verificando servicios..."
sleep 10

if docker-compose ps | grep -q "Up"; then
    echo_success "Servicios ejecutándose correctamente"
    echo ""
    echo "🎉 ¡Deployment completado!"
    echo "🌐 Tu dashboard está disponible en: https://$DOMAIN"
    echo ""
    echo "📋 Para monitorear los logs:"
    echo "   docker-compose logs -f"
    echo ""
    echo "🔄 Para actualizar la aplicación:"
    echo "   git pull && docker-compose build && docker-compose up -d"
else
    echo_error "Error en el deployment. Revisa los logs con: docker-compose logs"
    exit 1
fi

# 8. Configurar renovación automática de certificados
echo "🔄 Configurando renovación automática de certificados..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet --deploy-hook 'cd $(pwd) && sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem ./nginx/ssl/cert.pem && sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem ./nginx/ssl/key.pem && docker-compose restart nginx'") | crontab -
echo_success "Renovación automática configurada"

echo ""
echo "✨ ¡Todo listo! Tu dashboard está funcionando en producción."
