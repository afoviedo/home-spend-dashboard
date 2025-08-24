# 🏠 GUÍA DE DESPLIEGUE EN HOSTINGER VPS

## 📋 Requisitos previos

- **Hostinger VPS** con Ubuntu/Debian
- **Docker** y **Docker Compose** instalados
- **N8N** ya funcionando (opcional)
- **Dominio** apuntando al VPS (opcional pero recomendado)

## 🚀 Despliegue rápido en Hostinger

### 1. Preparar el VPS

```bash
# Conectar por SSH a tu VPS Hostinger
ssh root@tu-servidor-hostinger.com

# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker si no está instalado
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Clonar el proyecto

```bash
cd /home
git clone [URL-DE-TU-REPOSITORIO] home-spend-dashboard
cd home-spend-dashboard/deployment
```

### 3. Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar configuración
nano .env
```

**Configuración específica para Hostinger:**

```env
# OAuth Microsoft
AZURE_CLIENT_ID=tu-client-id-aqui
AZURE_CLIENT_SECRET=tu-client-secret-aqui
AZURE_TENANT_ID=tu-tenant-id-aqui
AZURE_REDIRECT_URI=https://tu-dominio.com/callback

# Configuración Hostinger
DOMAIN=tu-dominio.com
EMAIL=tu-email@gmail.com
ENVIRONMENT=production

# Puertos específicos (para evitar conflictos con N8N)
STREAMLIT_PORT=8502
NGINX_HTTP_PORT=8080
NGINX_HTTPS_PORT=8443

# Debug
DEBUG=false
```

### 4. Configurar dominio (opcional)

Si tienes un dominio, editar nginx:

```bash
nano nginx/nginx-hostinger.conf
```

Cambiar `tu-dominio.com` por tu dominio real.

### 5. Desplegar

```bash
# Hacer ejecutable el script
chmod +x deploy-hostinger.sh

# Ejecutar despliegue específico para Hostinger
./deploy-hostinger.sh
```

## 🔧 Administración diaria

### Panel de administración

```bash
# Hacer ejecutable
chmod +x admin-hostinger.sh

# Ejecutar panel interactivo
./admin-hostinger.sh

# O comandos directos
./admin-hostinger.sh status
./admin-hostinger.sh logs
./admin-hostinger.sh restart
```

### Comandos útiles para Hostinger

```bash
# Ver estado de todos los servicios
docker ps

# Ver logs del dashboard
docker-compose -f docker-compose-hostinger.yml logs -f dashboard

# Reiniciar solo el dashboard (N8N no se afecta)
docker-compose -f docker-compose-hostinger.yml restart dashboard

# Ver uso de recursos
docker stats

# Verificar puertos
sudo netstat -tlnp | grep LISTEN
```

## 🔗 URLs de acceso

### Con dominio configurado:
- **Dashboard:** https://tu-dominio.com
- **Callback OAuth:** https://tu-dominio.com/callback
- **Health Check:** https://tu-dominio.com/app-health

### Sin dominio (IP directa):
- **Dashboard:** http://IP-DE-TU-VPS:8502
- **Health Check:** http://IP-DE-TU-VPS:8502/_stcore/health

### N8N (si está configurado):
- **N8N:** http://IP-DE-TU-VPS:5678

## 🔒 Configuración SSL con Let's Encrypt

Si configuraste un dominio, el SSL se configurará automáticamente:

```bash
# Verificar certificados
docker-compose -f docker-compose-hostinger.yml exec certbot certbot certificates

# Renovar manualmente
docker-compose -f docker-compose-hostinger.yml exec certbot certbot renew --dry-run
```

## 🔄 Coexistencia con N8N

Esta configuración está optimizada para funcionar junto con N8N:

- **Dashboard:** Puertos 8502, 8080, 8443
- **N8N:** Puerto 5678 (habitual)
- **Red compartida:** Los servicios pueden comunicarse si es necesario

### Verificar coexistencia

```bash
# Ver todos los contenedores
docker ps

# Verificar puertos
sudo netstat -tlnp | grep LISTEN | grep -E "(5678|8502|8080|8443)"

# Verificar conflictos
./admin-hostinger.sh conflicts
```

## 🚨 Resolución de problemas

### Dashboard no arranca
```bash
# Ver logs detallados
docker-compose -f docker-compose-hostinger.yml logs dashboard

# Verificar configuración
./admin-hostinger.sh status

# Reiniciar
./admin-hostinger.sh restart
```

### Conflictos de puertos
```bash
# Ver qué usa cada puerto
sudo netstat -tlnp | grep LISTEN

# Cambiar puertos en docker-compose-hostinger.yml si es necesario
nano docker-compose-hostinger.yml
```

### Problemas de OAuth
1. Verificar URLs en Azure Portal
2. Confirmar AZURE_REDIRECT_URI en .env
3. Verificar conectividad HTTPS

### Memoria insuficiente
```bash
# Ver uso de recursos
free -h
docker stats

# Limpiar Docker
docker system prune -f

# Optimizar servicios
./admin-hostinger.sh cleanup
```

## 📊 Monitoreo

### Verificar salud del sistema
```bash
# Estado general
./admin-hostinger.sh status

# Logs en tiempo real
./admin-hostinger.sh logs

# Todos los servicios
./admin-hostinger.sh services
```

### Métricas importantes
- **CPU:** < 80% en promedio
- **Memoria:** < 80% del total
- **Disco:** < 90% de uso
- **Red:** Latencia < 100ms

## 🔄 Actualizaciones

### Actualizar dashboard
```bash
./admin-hostinger.sh update
```

### Actualizar Docker Compose
```bash
# Backup actual
./admin-hostinger.sh backup

# Actualizar archivos
git pull

# Reconstruir
docker-compose -f docker-compose-hostinger.yml up -d --build
```

## 💾 Backup y restauración

### Crear backup
```bash
./admin-hostinger.sh backup
```

### Backup manual completo
```bash
tar -czf backup-completo-$(date +%Y%m%d).tar.gz \
    .env \
    nginx/ \
    docker-compose-hostinger.yml \
    ../app/
```

### Restaurar
```bash
# Extraer backup
tar -xzf backup-dashboard-hostinger-YYYYMMDD_HHMMSS.tar.gz

# Reiniciar servicios
./admin-hostinger.sh restart
```

## 📞 Soporte

### Logs útiles para soporte
```bash
# Logs del dashboard
docker-compose -f docker-compose-hostinger.yml logs dashboard > dashboard-logs.txt

# Estado del sistema
./admin-hostinger.sh status > system-status.txt

# Configuración
cat .env > config.txt
```

### Información del sistema
```bash
# VPS info
uname -a
docker --version
docker-compose --version
df -h
free -h
```

---

🎉 **¡Tu dashboard ya está funcionando en Hostinger VPS!**

Accede a `https://tu-dominio.com` o `http://IP-VPS:8502` para empezar a usar tu dashboard de gastos del hogar.
