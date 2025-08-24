#!/bin/bash

# 🚀 DEPLOYMENT ESPECÍFICO PARA HOSTINGER VPS
# Dashboard de Gastos del Hogar con Docker

set -e

# ================================
# 🔧 CONFIGURACIÓN HOSTINGER
# ================================
DOMAIN="tu-dominio.com"           # ⚠️ CAMBIA POR TU DOMINIO REAL
EMAIL="tu-email@ejemplo.com"     # ⚠️ CAMBIA POR TU EMAIL REAL
APP_PORT="8502"                   # Puerto para evitar conflicto con N8N
PROJECT_NAME="home-spend-dashboard"

# ================================
# 🎨 COLORES
# ================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() { echo -e "${CYAN}$1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️ $1${NC}"; }

# ================================
# 🔍 VERIFICACIONES HOSTINGER
# ================================
print_header "🔍 Verificando configuración para Hostinger VPS..."

# Verificar dominio
if [ "$DOMAIN" = "tu-dominio.com" ]; then
    print_error "DEBES cambiar 'tu-dominio.com' por tu dominio real"
    exit 1
fi

# Verificar email
if [ "$EMAIL" = "tu-email@ejemplo.com" ]; then
    print_error "DEBES cambiar el email por tu email real"
    exit 1
fi

print_success "Configuración verificada para: $DOMAIN"

# ================================
# 🐳 VERIFICAR DOCKER EXISTENTE
# ================================
print_header "🐳 Verificando Docker existente..."

if ! command -v docker >/dev/null 2>&1; then
    print_error "Docker no encontrado. Instalando..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    print_warning "REINICIA TU SESIÓN SSH y ejecuta este script de nuevo"
    exit 0
fi

if ! command -v docker-compose >/dev/null 2>&1 && ! docker compose version >/dev/null 2>&1; then
    print_info "Instalando Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

print_success "Docker está listo"

# ================================
# 🔥 CONFIGURAR PUERTOS HOSTINGER
# ================================
print_header "🔥 Configurando puertos para Hostinger..."

# Hostinger generalmente tiene algunos puertos abiertos por defecto
# Verificar qué puertos están en uso
print_info "Puertos actualmente en uso:"
sudo netstat -tlnp | grep LISTEN | head -10

# Configurar firewall de Hostinger (ufw)
if command -v ufw >/dev/null 2>&1; then
    sudo ufw allow 22/tcp     # SSH
    sudo ufw allow 80/tcp     # HTTP
    sudo ufw allow 443/tcp    # HTTPS
    sudo ufw allow $APP_PORT/tcp  # Nuestra app
    sudo ufw --force enable
    print_success "Firewall configurado"
else
    print_warning "UFW no disponible, configurando iptables..."
    # Hostinger a veces usa iptables directamente
    sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
    sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
    sudo iptables -A INPUT -p tcp --dport $APP_PORT -j ACCEPT
fi

# ================================
# 📂 PREPARAR CONFIGURACIÓN
# ================================
print_header "📂 Preparando configuración para Hostinger..."

# Actualizar puerto en docker-compose para evitar conflictos con N8N
sed -i "s/8501:8501/$APP_PORT:8501/g" docker-compose.yml

# Actualizar configuración nginx
sed -i "s/tu-dominio.com/$DOMAIN/g" nginx/nginx.conf
sed -i "s/tu-email@ejemplo.com/$EMAIL/g" docker-compose.yml
sed -i "s/tu-dominio.com/$DOMAIN/g" docker-compose.yml

# Verificar archivo .env
if [ ! -f ".env" ]; then
    print_warning "Creando archivo .env desde plantilla..."
    cp .env.production .env
    sed -i "s/tu-dominio.com/$DOMAIN/g" .env
    
    print_error "⚠️ IMPORTANTE: Edita el archivo .env con tus credenciales de Microsoft Graph"
    print_info "Ejecuta: nano .env"
    print_info "Completa CLIENT_ID, CLIENT_SECRET, TENANT_ID"
    print_info "Presiona ENTER cuando hayas editado el archivo..."
    read -r
fi

print_success "Configuración preparada"

# ================================
# 🔒 SSL PARA HOSTINGER
# ================================
print_header "🔒 Configurando SSL en Hostinger..."

# Crear directorios
mkdir -p nginx/ssl nginx/certbot-webroot

# Verificar DNS
print_info "Verificando DNS para $DOMAIN..."
SERVER_IP=$(curl -s https://ipinfo.io/ip)
DOMAIN_IP=$(dig +short $DOMAIN | tail -n1)

print_info "IP del servidor: $SERVER_IP"
print_info "IP del dominio: $DOMAIN_IP"

if [ "$SERVER_IP" != "$DOMAIN_IP" ]; then
    print_warning "⚠️ El dominio podría no apuntar correctamente al servidor"
    print_info "¿Continuar de todas formas? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Obtener certificados SSL
print_info "Obteniendo certificados SSL..."

# Verificar si hay servicios en puerto 80
if sudo netstat -tlnp | grep -q ":80 "; then
    print_warning "Puerto 80 ocupado. Liberando temporalmente..."
    # Hostinger a veces tiene servicios en puerto 80
    sudo systemctl stop nginx 2>/dev/null || true
    sudo systemctl stop apache2 2>/dev/null || true
fi

# Obtener certificados usando Certbot standalone
if command -v certbot >/dev/null 2>&1; then
    sudo certbot certonly --standalone \
        --email $EMAIL \
        --agree-tos \
        --no-eff-email \
        -d $DOMAIN
else
    # Instalar certbot
    sudo apt update
    sudo apt install -y certbot
    sudo certbot certonly --standalone \
        --email $EMAIL \
        --agree-tos \
        --no-eff-email \
        -d $DOMAIN
fi

# Copiar certificados
if [ -d "/etc/letsencrypt/live/$DOMAIN" ]; then
    sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem nginx/ssl/cert.pem
    sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem nginx/ssl/key.pem
    sudo chown $USER:$USER nginx/ssl/*
    print_success "Certificados SSL configurados"
else
    print_warning "Creando certificados auto-firmados temporales..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/key.pem \
        -out nginx/ssl/cert.pem \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=$DOMAIN"
fi

# ================================
# 🐳 DEPLOYMENT CON DOCKER
# ================================
print_header "🐳 Desplegando con Docker en Hostinger..."

# Verificar si hay contenedores N8N corriendo y sus puertos
print_info "Verificando contenedores existentes..."
docker ps --format "table {{.Names}}\t{{.Ports}}\t{{.Status}}"

# Detener contenedores previos del dashboard si existen
docker-compose down 2>/dev/null || true

# Limpiar imágenes previas
print_info "Limpiando imágenes previas..."
docker image prune -f

# Construir con cache limpio
print_info "Construyendo aplicación..."
docker-compose build --no-cache

# Iniciar servicios
print_info "Iniciando servicios..."
docker-compose up -d

# Esperar inicio
print_info "Esperando a que los servicios inicien..."
sleep 30

# ================================
# ✅ VERIFICACIÓN HOSTINGER
# ================================
print_header "✅ Verificando deployment en Hostinger..."

# Verificar contenedores
if docker-compose ps | grep -q "Up"; then
    print_success "Contenedores funcionando correctamente"
    
    # Mostrar información específica de Hostinger
    print_info "Información del deployment:"
    echo "  📊 Dashboard: https://$DOMAIN"
    echo "  🔄 OAuth: https://$DOMAIN/callback"
    echo "  🏠 Local: http://$(hostname -I | awk '{print $1}'):$APP_PORT"
    echo "  🐳 Contenedores:"
    docker-compose ps
    
else
    print_error "Error en deployment. Verificando logs..."
    docker-compose logs --tail=20
fi

# Verificar conectividad
print_info "Verificando conectividad..."
if curl -s -f http://localhost:$APP_PORT/_stcore/health >/dev/null 2>&1; then
    print_success "Dashboard respondiendo en puerto $APP_PORT"
else
    print_warning "Dashboard aún iniciando... Verificar logs:"
    docker-compose logs dashboard --tail=10
fi

# ================================
# 🔄 CONFIGURAR MANTENIMIENTO
# ================================
print_header "🔄 Configurando mantenimiento automático..."

# Script de renovación para Hostinger
cat > /usr/local/bin/renew-certs-hostinger.sh << EOF
#!/bin/bash
cd $(pwd)
# Parar nginx temporalmente
docker-compose stop nginx
# Renovar certificados
sudo certbot renew --standalone
if [ \$? -eq 0 ]; then
    sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem nginx/ssl/cert.pem
    sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem nginx/ssl/key.pem
    sudo chown $USER:$USER nginx/ssl/*
    docker-compose start nginx
fi
EOF

sudo chmod +x /usr/local/bin/renew-certs-hostinger.sh

# Cron para renovación
(crontab -l 2>/dev/null; echo "0 3 1 * * /usr/local/bin/renew-certs-hostinger.sh >> /var/log/cert-renew.log 2>&1") | crontab -

print_success "Renovación automática configurada"

# ================================
# 🎉 FINALIZACIÓN HOSTINGER
# ================================
print_header "🎉 ¡DEPLOYMENT EN HOSTINGER COMPLETADO!"

echo ""
print_success "Dashboard desplegado exitosamente en Hostinger VPS"
echo ""
print_info "📊 URLs de tu dashboard:"
echo "  • Producción: https://$DOMAIN"
echo "  • Callback OAuth: https://$DOMAIN/callback"
echo "  • Acceso directo: http://$(hostname -I | awk '{print $1}'):$APP_PORT"
echo ""
print_info "🐳 Contenedores activos:"
docker-compose ps
echo ""
print_info "🔗 Junto con N8N y otros servicios Docker existentes"
echo ""
print_header "📋 Comandos para administración:"
echo ""
echo "  # Ver estado:"
echo "  ./admin.sh status"
echo ""
echo "  # Ver logs:"
echo "  ./admin.sh logs"
echo ""
echo "  # Reiniciar:"
echo "  ./admin.sh restart"
echo ""
echo "  # Actualizar:"
echo "  ./admin.sh update"
echo ""
print_header "⚠️ IMPORTANTE - Configuración final:"
print_warning "1. Edita .env con tus credenciales de Microsoft Graph"
print_warning "2. Agrega https://$DOMAIN/callback como Redirect URI en Azure Portal"
print_warning "3. Verifica que el dominio apunte correctamente al VPS"
echo ""
print_success "¡Tu dashboard está listo en Hostinger junto con N8N! 🚀"
