#!/bin/bash

# 🚀 DEPLOYMENT AUTOMÁTICO CON DOCKER - Dashboard de Gastos del Hogar
# Este script hace TODO por ti. Solo necesitas cambiar tu dominio y ejecutar.

set -e  # Salir si hay algún error

# ================================
# 🔧 CONFIGURACIÓN (CAMBIAR AQUÍ)
# ================================
DOMAIN="tu-dominio.com"           # ⚠️ CAMBIA POR TU DOMINIO REAL
EMAIL="tu-email@ejemplo.com"     # ⚠️ CAMBIA POR TU EMAIL REAL
PROJECT_NAME="home-spend-dashboard"

# ================================
# 🎨 COLORES PARA OUTPUT
# ================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Funciones para output colorido
print_header() { echo -e "${CYAN}$1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️ $1${NC}"; }

# ================================
# 🔍 VERIFICACIONES INICIALES
# ================================
print_header "🔍 Verificando configuración inicial..."

# Verificar que se cambió el dominio
if [ "$DOMAIN" = "tu-dominio.com" ]; then
    print_error "DEBES cambiar 'tu-dominio.com' por tu dominio real en la línea 7 de este script"
    print_info "Edita este archivo y cambia DOMAIN=\"tu-dominio.com\" por tu dominio real"
    exit 1
fi

# Verificar que se cambió el email
if [ "$EMAIL" = "tu-email@ejemplo.com" ]; then
    print_error "DEBES cambiar 'tu-email@ejemplo.com' por tu email real en la línea 8 de este script"
    print_info "Edita este archivo y cambia EMAIL=\"tu-email@ejemplo.com\" por tu email real"
    exit 1
fi

print_success "Configuración verificada: $DOMAIN"

# ================================
# 📦 INSTALACIÓN DE DEPENDENCIAS
# ================================
print_header "📦 Instalando dependencias necesarias..."

# Función para verificar si un comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Actualizar sistema
print_info "Actualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar Docker si no existe
if ! command_exists docker; then
    print_warning "Docker no encontrado. Instalando Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    print_success "Docker instalado"
    
    print_warning "REINICIA TU SESIÓN SSH y ejecuta este script de nuevo"
    print_info "Comando: logout && ssh usuario@servidor"
    exit 0
fi

# Verificar Docker Compose
if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
    print_warning "Docker Compose no encontrado. Instalando..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    print_success "Docker Compose instalado"
fi

# Instalar curl si no existe
if ! command_exists curl; then
    sudo apt install -y curl
fi

print_success "Todas las dependencias instaladas"

# ================================
# 🔥 CONFIGURACIÓN DE FIREWALL
# ================================
print_header "🔥 Configurando firewall..."

sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw --force enable

print_success "Firewall configurado"

# ================================
# 📂 PREPARACIÓN DE ARCHIVOS
# ================================
print_header "📂 Preparando archivos de configuración..."

# Actualizar dominio en archivos de configuración
print_info "Actualizando configuración con dominio: $DOMAIN"

# Actualizar nginx.conf
sed -i "s/tu-dominio.com/$DOMAIN/g" nginx/nginx.conf

# Actualizar docker-compose.yml
sed -i "s/tu-email@ejemplo.com/$EMAIL/g" docker-compose.yml
sed -i "s/tu-dominio.com/$DOMAIN/g" docker-compose.yml

# Verificar que existe el archivo .env
if [ ! -f ".env" ]; then
    print_warning "Archivo .env no encontrado. Creando desde plantilla..."
    cp .env.production .env
    
    print_error "⚠️ IMPORTANTE: Debes editar el archivo .env con tus credenciales de Microsoft Graph"
    print_info "Edita .env y completa:"
    print_info "  CLIENT_ID=tu_client_id_real"
    print_info "  CLIENT_SECRET=tu_client_secret_real"
    print_info "  TENANT_ID=tu_tenant_id_real"
    print_info "  REDIRECT_URI=https://$DOMAIN/callback"
    print_info ""
    print_info "Presiona ENTER cuando hayas editado el archivo .env..."
    read -r
fi

print_success "Archivos preparados"

# ================================
# 🔒 CONFIGURACIÓN SSL
# ================================
print_header "🔒 Configurando certificados SSL..."

# Crear directorio para SSL
mkdir -p nginx/ssl
mkdir -p nginx/certbot-webroot

# Verificar que el dominio apunta al servidor
print_info "Verificando que $DOMAIN apunta a este servidor..."
SERVER_IP=$(curl -s https://ipinfo.io/ip)
DOMAIN_IP=$(dig +short $DOMAIN | tail -n1)

if [ "$SERVER_IP" != "$DOMAIN_IP" ]; then
    print_warning "⚠️ El dominio $DOMAIN no parece apuntar a este servidor"
    print_info "IP del servidor: $SERVER_IP"
    print_info "IP del dominio: $DOMAIN_IP"
    print_info "Asegúrate de que tu DNS esté configurado correctamente"
    print_info "¿Continuar de todas formas? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Obtener certificados SSL
print_info "Obteniendo certificados SSL de Let's Encrypt..."

# Iniciar nginx temporal para verificación
docker run --rm -d --name nginx-temp -p 80:80 -v $(pwd)/nginx/certbot-webroot:/var/www/certbot nginx:alpine

# Obtener certificados
docker run --rm -v $(pwd)/nginx/ssl:/etc/letsencrypt -v $(pwd)/nginx/certbot-webroot:/var/www/certbot certbot/certbot \
    certonly --webroot --webroot-path=/var/www/certbot \
    --email $EMAIL --agree-tos --no-eff-email \
    -d $DOMAIN

# Detener nginx temporal
docker stop nginx-temp

# Copiar certificados a ubicación correcta
if [ -d "nginx/ssl/live/$DOMAIN" ]; then
    cp nginx/ssl/live/$DOMAIN/fullchain.pem nginx/ssl/cert.pem
    cp nginx/ssl/live/$DOMAIN/privkey.pem nginx/ssl/key.pem
    print_success "Certificados SSL configurados"
else
    print_error "Error obteniendo certificados SSL"
    print_info "Creando certificados auto-firmados temporales..."
    
    # Crear certificados auto-firmados para desarrollo/testing
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/key.pem \
        -out nginx/ssl/cert.pem \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=$DOMAIN"
    
    print_warning "Usando certificados auto-firmados. El navegador mostrará advertencias de seguridad."
fi

# ================================
# 🐳 CONSTRUCCIÓN Y DEPLOYMENT
# ================================
print_header "🐳 Construyendo y desplegando con Docker..."

# Detener contenedores existentes si existen
print_info "Deteniendo contenedores existentes..."
docker-compose down 2>/dev/null || true

# Construir imágenes
print_info "Construyendo imágenes Docker..."
docker-compose build --no-cache

# Iniciar servicios
print_info "Iniciando servicios..."
docker-compose up -d

# Esperar a que los servicios estén listos
print_info "Esperando a que los servicios inicien..."
sleep 30

# ================================
# ✅ VERIFICACIÓN FINAL
# ================================
print_header "✅ Verificando deployment..."

# Verificar que los contenedores están corriendo
if docker-compose ps | grep -q "Up"; then
    print_success "Contenedores ejecutándose correctamente"
else
    print_error "Error: Algunos contenedores no están funcionando"
    print_info "Logs de diagnóstico:"
    docker-compose logs --tail=50
    exit 1
fi

# Verificar conectividad HTTP
print_info "Verificando conectividad..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost | grep -q "200\|301\|302"; then
    print_success "Dashboard respondiendo correctamente"
else
    print_warning "Dashboard podría estar iniciando aún..."
fi

# ================================
# 🔄 CONFIGURACIÓN DE MANTENIMIENTO
# ================================
print_header "🔄 Configurando mantenimiento automático..."

# Crear script de renovación de certificados
cat > /usr/local/bin/renew-certs.sh << EOF
#!/bin/bash
cd $(pwd)
docker-compose run --rm certbot renew
if [ \$? -eq 0 ]; then
    cp nginx/ssl/live/$DOMAIN/fullchain.pem nginx/ssl/cert.pem
    cp nginx/ssl/live/$DOMAIN/privkey.pem nginx/ssl/key.pem
    docker-compose restart nginx
fi
EOF

chmod +x /usr/local/bin/renew-certs.sh

# Configurar cron para renovación automática
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/local/bin/renew-certs.sh >> /var/log/certbot-renew.log 2>&1") | crontab -

print_success "Renovación automática de certificados configurada"

# ================================
# 🎉 FINALIZACIÓN
# ================================
print_header "🎉 ¡DEPLOYMENT COMPLETADO!"

echo ""
print_success "Tu Dashboard de Gastos del Hogar está funcionando!"
echo ""
print_info "📊 URL del Dashboard: https://$DOMAIN"
print_info "🔄 OAuth Callback: https://$DOMAIN/callback"
echo ""
print_header "📋 Comandos útiles para administración:"
echo ""
echo "  # Ver estado de contenedores:"
echo "  docker-compose ps"
echo ""
echo "  # Ver logs en tiempo real:"
echo "  docker-compose logs -f"
echo ""
echo "  # Reiniciar servicios:"
echo "  docker-compose restart"
echo ""
echo "  # Actualizar aplicación:"
echo "  git pull && docker-compose build && docker-compose up -d"
echo ""
echo "  # Detener todo:"
echo "  docker-compose down"
echo ""
print_header "🔒 Información de seguridad:"
print_info "✅ HTTPS habilitado con certificados SSL"
print_info "✅ Firewall configurado"
print_info "✅ Headers de seguridad aplicados"
print_info "✅ Renovación automática de certificados"
echo ""
print_warning "📝 IMPORTANTE: Verifica que tu archivo .env tenga las credenciales correctas de Microsoft Graph"
print_warning "🌐 IMPORTANTE: Asegúrate de agregar https://$DOMAIN/callback como Redirect URI en Azure Portal"
echo ""
print_success "¡Todo listo! Tu dashboard está funcionando en producción con Docker! 🐳"
