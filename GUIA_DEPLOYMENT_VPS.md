# 🚀 Guía Completa: Hostear Dashboard en VPS

## 📋 Resumen de Opciones

### **Opción 1: Deployment con Docker (Recomendado) 🐳**
- ✅ Fácil de escalar y mantener
- ✅ Aislamiento completo
- ✅ SSL automático con Let's Encrypt
- ✅ Nginx como proxy reverso

### **Opción 2: Deployment Simple (Nativo) 🖥️**
- ✅ Menor uso de recursos
- ✅ Configuración directa en el servidor
- ✅ Ideal para VPS pequeños

### **Opción 3: Azure App Service 🌟**
- ✅ Managed service
- ✅ Escalado automático
- ✅ Integración directa con Azure

## 🔧 OPCIÓN 1: Deployment con Docker

### Paso 1: Preparar el VPS

```bash
# Conectar al VPS
ssh usuario@tu-vps-ip

# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Clonar tu repositorio
git clone https://github.com/tu-usuario/home-spend-dashboard.git
cd home-spend-dashboard
```

### Paso 2: Configurar OAuth para producción

En **Azure Portal** (portal.azure.com):

1. Ve a **App registrations** → Tu aplicación
2. **Authentication** → **Platform configurations** 
3. Agregar **Redirect URI**: `https://tu-dominio.com/callback`

### Paso 3: Configurar variables de entorno

```bash
# Copiar configuración de producción
cp deployment/.env.production .env

# Editar con tus datos reales
nano .env
```

Completar:
```env
CLIENT_ID=tu_application_client_id
CLIENT_SECRET=tu_application_client_secret  
TENANT_ID=tu_tenant_id
REDIRECT_URI=https://tu-dominio.com/callback
```

### Paso 4: Ejecutar deployment automático

```bash
# Ir al directorio de deployment
cd deployment

# Editar script con tu dominio
sed -i 's/tu-dominio.com/TU_DOMINIO_REAL.com/g' deploy.sh

# Hacer ejecutable y ejecutar
chmod +x deploy.sh
./deploy.sh
```

### Paso 5: Verificar

- **Dashboard:** `https://tu-dominio.com`
- **Logs:** `docker-compose logs -f`

---

## 🖥️ OPCIÓN 2: Deployment Simple (Sin Docker)

### Comando único de instalación:

```bash
# Descargar y ejecutar script
curl -O https://raw.githubusercontent.com/tu-repo/deployment/deploy-simple.sh
chmod +x deploy-simple.sh

# Editar con tu dominio antes de ejecutar
nano deploy-simple.sh  # Cambiar tu-dominio.com

# Ejecutar
./deploy-simple.sh
```

### Comandos de administración:

```bash
# Ver estado del servicio
sudo systemctl status home-spend-dashboard

# Ver logs en tiempo real
sudo journalctl -u home-spend-dashboard -f

# Reiniciar servicio
sudo systemctl restart home-spend-dashboard

# Actualizar aplicación
cd /opt/home-spend-dashboard
git pull
sudo systemctl restart home-spend-dashboard
```

---

## 🌟 OPCIÓN 3: Azure App Service

### Ventajas:
- Managed service (sin administración de servidor)
- SSL automático
- Escalado automático
- Integración nativa con Azure AD

### Pasos:

1. **Crear App Service en Azure Portal**
2. **Configurar deployment desde GitHub**
3. **Configurar variables de entorno en Azure**
4. **El deployment es automático**

---

## 🔧 Configuraciones Importantes

### 1. Variables de Entorno de Producción

```env
# OAuth Microsoft Graph
CLIENT_ID=tu_application_client_id
CLIENT_SECRET=tu_application_client_secret
TENANT_ID=tu_tenant_id  
REDIRECT_URI=https://tu-dominio.com/callback

# Configuración App
ENVIRONMENT=production
DEBUG=false
ONEDRIVE_FOLDER_PATH=/Casa

# Seguridad
SESSION_SECRET=genera_clave_secreta_aleatoria
```

### 2. Configuración DNS

Apuntar tu dominio al VPS:
```
Tipo: A
Nombre: @ (o dashboard)
Valor: IP_DE_TU_VPS
TTL: 300
```

### 3. Firewall (Ubuntu/Debian)

```bash
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

## 🔍 Troubleshooting

### Dashboard no carga:
```bash
# Verificar logs
docker-compose logs dashboard
# O para deployment simple:
sudo journalctl -u home-spend-dashboard -f
```

### Error de OAuth:
1. Verificar REDIRECT_URI en Azure Portal
2. Verificar variables en `.env`
3. Verificar que el dominio esté funcionando

### Error de SSL:
```bash
# Verificar certificados
sudo certbot certificates

# Renovar manualmente
sudo certbot renew
```

## 📊 Monitoreo y Mantenimiento

### Comandos útiles:

```bash
# Docker
docker-compose ps                    # Estado de contenedores
docker-compose logs -f               # Logs en tiempo real
docker-compose restart               # Reiniciar servicios

# Simple deployment  
sudo systemctl status home-spend-dashboard    # Estado
sudo systemctl restart home-spend-dashboard   # Reiniciar
sudo journalctl -u home-spend-dashboard -f    # Logs
```

### Actualización:

```bash
# Para Docker
git pull
docker-compose build
docker-compose up -d

# Para deployment simple
cd /opt/home-spend-dashboard
git pull
sudo systemctl restart home-spend-dashboard
```

## 💡 Recomendaciones Finales

1. **Usa un dominio real** - No funciona bien con IPs
2. **Configura backups** - De la configuración y datos
3. **Monitorea logs** - Para detectar problemas temprano
4. **Actualiza regularmente** - Sistema operativo y dependencias
5. **Usa HTTPS siempre** - Microsoft Graph requiere SSL

## 🆘 Soporte

Si tienes problemas:

1. **Revisa logs** detalladamente
2. **Verifica variables de entorno**
3. **Confirma configuración de Azure AD**
4. **Prueba conectividad** (ping, curl)

---

**¡Tu dashboard estará funcionando en producción en minutos!** 🎉
