# Dashboard de Gastos del Hogar - Deployment en VPS

## 🚀 Guía de Deployment en VPS

### Prerrequisitos

1. **VPS con Ubuntu/Debian** (recomendado: Ubuntu 22.04 LTS)
2. **Dominio apuntando a tu VPS** (ejemplo: dashboard.tudominio.com)
3. **Credenciales de Microsoft Graph API**
4. **Acceso SSH al VPS**

### 📋 Pasos de Instalación

#### 1. Preparar el VPS

```bash
# Conectar al VPS
ssh usuario@tu-vps-ip

# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Git
sudo apt install -y git curl
```

#### 2. Clonar el proyecto

```bash
# Clonar desde tu repositorio
git clone https://github.com/tu-usuario/home-spend-dashboard.git
cd home-spend-dashboard
```

#### 3. Configurar OAuth para producción

En el **Azure Portal** (portal.azure.com):

1. Ve a **App registrations** → Tu aplicación
2. En **Authentication** → **Platform configurations**
3. Agrega nueva **Redirect URI**:
   - `https://tu-dominio.com/callback`
4. Guarda los cambios

#### 4. Configurar variables de entorno

```bash
# Copiar plantilla de configuración
cp deployment/.env.production .env

# Editar con tus datos reales
nano .env
```

Completa con tus datos:
```env
CLIENT_ID=tu_application_client_id
CLIENT_SECRET=tu_application_client_secret
TENANT_ID=tu_tenant_id
REDIRECT_URI=https://tu-dominio.com/callback
```

#### 5. Ejecutar deployment automático

```bash
# Hacer ejecutable el script
chmod +x deployment/deploy.sh

# Ejecutar deployment
./deployment/deploy.sh
```

### 🔧 Configuración Manual (Alternativa)

Si prefieres configurar manualmente:

#### Instalar Docker y Docker Compose

```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Reiniciar sesión para aplicar cambios
logout
```

#### Configurar SSL con Let's Encrypt

```bash
# Instalar Certbot
sudo apt install -y certbot

# Obtener certificados
sudo certbot certonly --standalone -d tu-dominio.com --email tu-email@ejemplo.com --agree-tos

# Copiar certificados
mkdir -p deployment/nginx/ssl
sudo cp /etc/letsencrypt/live/tu-dominio.com/fullchain.pem deployment/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/tu-dominio.com/privkey.pem deployment/nginx/ssl/key.pem
sudo chown $USER:$USER deployment/nginx/ssl/*
```

#### Ejecutar con Docker Compose

```bash
# Ir al directorio de deployment
cd deployment

# Construir y ejecutar
docker-compose up -d

# Ver logs
docker-compose logs -f
```

### 🔍 Verificación y Monitoreo

#### Comandos útiles:

```bash
# Ver estado de contenedores
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f

# Reiniciar servicios
docker-compose restart

# Actualizar aplicación
git pull
docker-compose build
docker-compose up -d
```

#### URLs importantes:

- **Dashboard:** `https://tu-dominio.com`
- **OAuth Callback:** `https://tu-dominio.com/callback`

### 🔒 Seguridad

El deployment incluye:

- ✅ **HTTPS obligatorio** con certificados SSL automáticos
- ✅ **Firewall configurado** (puertos 22, 80, 443)
- ✅ **Headers de seguridad** (X-Frame-Options, X-XSS-Protection)
- ✅ **Renovación automática** de certificados SSL
- ✅ **Proxy reverso** con Nginx
- ✅ **Variables de entorno** para credenciales sensibles

### 🔄 Mantenimiento

#### Renovar certificados SSL:
```bash
sudo certbot renew
docker-compose restart nginx
```

#### Actualizar aplicación:
```bash
cd /path/to/your/app
git pull
docker-compose build
docker-compose up -d
```

#### Backup de datos:
```bash
# Backup de configuración
tar -czf backup-$(date +%Y%m%d).tar.gz .env deployment/nginx/ssl
```

### 🆘 Troubleshooting

#### Si el dashboard no carga:
```bash
# Verificar logs
docker-compose logs dashboard

# Verificar conectividad
curl -I http://localhost:8501
```

#### Si OAuth falla:
1. Verificar REDIRECT_URI en Azure Portal
2. Verificar variables de entorno en `.env`
3. Verificar logs: `docker-compose logs dashboard`

#### Si SSL no funciona:
```bash
# Verificar certificados
sudo certbot certificates

# Verificar configuración de nginx
docker-compose logs nginx
```

### 💡 Consejos adicionales

1. **Monitoreo:** Configura alertas para el estado del servidor
2. **Backup:** Programa backups automáticos de la configuración
3. **Updates:** Mantén Docker y el sistema operativo actualizados
4. **Logs:** Revisa logs regularmente para detectar problemas
5. **Performance:** Considera usar un CDN para mejor rendimiento global
