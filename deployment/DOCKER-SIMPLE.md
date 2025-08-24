# 🐳 GUÍA SÚPER SIMPLE - Deployment con Docker

## ¿Por qué Docker? 🤔

Docker es como una "caja mágica" que:
- ✅ **Funciona igual en cualquier servidor** (Ubuntu, CentOS, etc.)
- ✅ **Nunca se rompe** por actualizaciones del sistema
- ✅ **Es fácil de actualizar** y hacer backup
- ✅ **Se administra solo** - SSL automático, reinicio automático
- ✅ **No necesitas saber Linux** para usarlo

## 🚀 Instalación en 3 pasos

### Paso 1: Subir archivos a tu VPS

```bash
# Conectar a tu VPS
ssh usuario@tu-vps-ip

# Clonar o subir el proyecto
git clone https://github.com/tu-usuario/home-spend-dashboard.git
cd home-spend-dashboard/deployment
```

### Paso 2: Configurar tu dominio

```bash
# Editar el script de deployment
nano deploy-docker-auto.sh

# Cambiar estas líneas (al principio del archivo):
DOMAIN="tu-dominio.com"       # ← Cambiar por tu dominio real
EMAIL="tu-email@ejemplo.com"  # ← Cambiar por tu email real
```

### Paso 3: Ejecutar y ¡listo!

```bash
# Hacer ejecutable y ejecutar
chmod +x deploy-docker-auto.sh
./deploy-docker-auto.sh
```

**¡Eso es todo!** El script hace todo automáticamente:
- Instala Docker
- Configura SSL
- Configura firewall
- Despliega la aplicación
- Configura renovación automática de certificados

## 📱 Administración súper fácil

Usa el panel de administración:

```bash
# Panel interactivo
./admin.sh

# O comandos directos
./admin.sh status    # Ver estado
./admin.sh logs      # Ver logs
./admin.sh restart   # Reiniciar
./admin.sh update    # Actualizar
```

## ⚙️ Configuración Azure AD

Antes de ejecutar, configura en Azure Portal:

1. Ve a **App registrations** → Tu aplicación
2. **Authentication** → **Platform configurations**
3. Agregar **Redirect URI**: `https://tu-dominio.com/callback`

## 📝 Configurar variables de entorno

Edita el archivo `.env`:

```env
CLIENT_ID=tu_application_client_id
CLIENT_SECRET=tu_application_client_secret
TENANT_ID=tu_tenant_id
REDIRECT_URI=https://tu-dominio.com/callback
```

## 🔧 Comandos útiles

### Ver estado
```bash
./admin.sh status
```

### Ver logs en tiempo real
```bash
./admin.sh logs
```

### Reiniciar servicios
```bash
./admin.sh restart
```

### Actualizar aplicación
```bash
./admin.sh update
```

### Hacer backup
```bash
./admin.sh backup
```

### Parar todo
```bash
./admin.sh stop
```

### Iniciar todo
```bash
./admin.sh start
```

## 🆘 Si algo sale mal

### Dashboard no carga:
```bash
./admin.sh logs  # Ver qué está pasando
```

### OAuth no funciona:
1. Verifica REDIRECT_URI en Azure Portal
2. Verifica variables en `.env`
3. Verifica que tu dominio funcione

### Certificados SSL fallan:
- Verifica que tu dominio apunte al VPS
- Espera unos minutos y reintenta

## 📊 Estructura de archivos

```
deployment/
├── 🐳 docker-compose.yml     # Configuración de servicios
├── 🐳 Dockerfile             # Imagen de la aplicación
├── 🌐 nginx/                 # Configuración del proxy
├── 🚀 deploy-docker-auto.sh  # Script de instalación automática
├── 🎛️ admin.sh              # Panel de administración
├── 📋 .env                   # Variables de entorno
└── 📚 README.md              # Esta guía
```

## 🔒 Seguridad incluida

El deployment automáticamente configura:

- ✅ **HTTPS obligatorio** con certificados gratuitos
- ✅ **Firewall** configurado automáticamente  
- ✅ **Headers de seguridad** 
- ✅ **Renovación automática** de certificados
- ✅ **Rate limiting** para prevenir ataques
- ✅ **Logs** para monitoreo

## 🎯 URLs importantes

Después del deployment:

- **📊 Dashboard:** `https://tu-dominio.com`
- **🔄 OAuth:** `https://tu-dominio.com/callback`
- **🏥 Health:** `https://tu-dominio.com/health`

## 💡 Ventajas de esta solución Docker

### vs Instalación manual:
- ✅ **No se rompe** con actualizaciones del sistema
- ✅ **Backup fácil** - solo archivos de configuración
- ✅ **Portabilidad** - funciona en cualquier servidor

### vs Azure App Service:
- ✅ **Más barato** - usas tu propio VPS
- ✅ **Control total** sobre la configuración
- ✅ **Sin límites** de Azure

### vs Instalación nativa:
- ✅ **Aislamiento** - no contamina el sistema
- ✅ **Fácil limpieza** - `docker-compose down`
- ✅ **Versionado** - puedes volver a versiones anteriores

## 🔄 Proceso de actualización

Para actualizar tu dashboard:

```bash
./admin.sh update
```

Esto automáticamente:
1. Hace backup de tu configuración
2. Descarga nuevos cambios
3. Reconstruye la aplicación
4. Reinicia servicios
5. Verifica que todo funcione

## 📱 Monitoreo

### Ver uso de recursos:
```bash
./admin.sh status
```

### Ver logs detallados:
```bash
./admin.sh logs
```

### Verificar conectividad:
```bash
curl -I https://tu-dominio.com/health
```

## 🆘 Troubleshooting común

### Error: "Puerto 80 ocupado"
```bash
sudo netstat -tlnp | grep :80
sudo systemctl stop apache2  # Si tienes Apache
```

### Error: "Dominio no resuelve"
- Verifica que tu DNS apunte al VPS
- Usa herramientas como `dig tu-dominio.com`

### Error: "Certificados SSL fallan"
- Verifica conectividad en puerto 80
- Asegúrate que no hay otros servicios web

### Dashboard lento:
```bash
# Ver uso de recursos
docker stats
```

## 🎉 ¡Todo listo!

Con esta configuración Docker tienes:

- 🚀 **Deployment automático** en un comando
- 🎛️ **Administración fácil** con panel visual
- 🔒 **Seguridad enterprise** 
- 🔄 **Actualizaciones simples**
- 💾 **Backups automáticos**
- 📊 **Monitoreo incluido**

**¡No necesitas saber Docker para usarlo, todo está automatizado!** 🐳✨
