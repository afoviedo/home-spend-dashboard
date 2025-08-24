# 📋 CHECKLIST DE DESPLIEGUE EN HOSTINGER VPS

## ✅ Pre-despliegue

### 🏠 Preparación del VPS Hostinger
- [ ] Acceso SSH al VPS configurado
- [ ] Docker instalado y funcionando
- [ ] Docker Compose instalado
- [ ] Git instalado
- [ ] Dominio apuntando al VPS (opcional)
- [ ] Puertos disponibles: 8502, 8080, 8443

### 🔐 Configuración OAuth Microsoft
- [ ] App registrada en Azure Portal
- [ ] Client ID obtenido
- [ ] Client Secret generado
- [ ] Tenant ID identificado
- [ ] URL de callback configurada: `https://tu-dominio.com/callback`
- [ ] Permisos de Microsoft Graph asignados

### 📁 Preparación del proyecto
- [ ] Código clonado en el VPS
- [ ] Archivo `.env` configurado desde `.env.hostinger`
- [ ] Variables de entorno verificadas
- [ ] Permisos de archivos configurados

## 🚀 Despliegue

### 1️⃣ Configuración inicial
```bash
# En tu VPS Hostinger
cd /home
git clone [TU-REPOSITORIO] home-spend-dashboard
cd home-spend-dashboard/deployment
cp .env.hostinger .env
nano .env  # Configurar variables reales
```

### 2️⃣ Configuración de dominio
```bash
# Solo si tienes dominio
nano nginx/nginx-hostinger.conf
# Cambiar 'tu-dominio.com' por tu dominio real
```

### 3️⃣ Permisos
```bash
chmod +x deploy-hostinger.sh
chmod +x admin-hostinger.sh
```

### 4️⃣ Despliegue
```bash
./deploy-hostinger.sh
```

### 5️⃣ Verificación
```bash
./admin-hostinger.sh status
```

## ✅ Post-despliegue

### 🔍 Verificaciones básicas
- [ ] Dashboard accesible en `http://IP:8502`
- [ ] Nginx funcionando en puerto 8080
- [ ] SSL configurado (si usas dominio)
- [ ] Health check respondiendo: `http://IP:8502/_stcore/health`
- [ ] N8N sigue funcionando (si estaba instalado)

### 🔒 Verificaciones de seguridad
- [ ] OAuth funcionando correctamente
- [ ] Callback URL accesible
- [ ] Headers de seguridad activos
- [ ] HTTPS forzado (si usas dominio)

### 📊 Verificaciones de rendimiento
- [ ] Uso de CPU < 80%
- [ ] Uso de memoria < 80%
- [ ] Espacio en disco suficiente
- [ ] Logs sin errores críticos

## 🔧 Configuración avanzada

### 🌐 Con dominio personalizado
- [ ] DNS A record apuntando al VPS
- [ ] Certificado SSL generado automáticamente
- [ ] HTTPS funcionando: `https://tu-dominio.com`
- [ ] Redirección HTTP -> HTTPS activa

### 🤖 Coexistencia con N8N
- [ ] N8N sigue accesible en puerto 5678
- [ ] No hay conflictos de puertos
- [ ] Ambos servicios funcionan simultáneamente
- [ ] Red Docker compartida configurada (si es necesario)

### 💾 Backup configurado
- [ ] Script de backup funcionando
- [ ] Directorio de backups creado
- [ ] Backup inicial realizado
- [ ] Procedimiento de restauración probado

## 🚨 Resolución de problemas

### ❌ Dashboard no arranca
```bash
# Verificar logs
docker-compose -f docker-compose-hostinger.yml logs dashboard

# Verificar configuración
./admin-hostinger.sh status

# Reiniciar
./admin-hostinger.sh restart
```

### ❌ OAuth no funciona
- [ ] URLs en Azure Portal correctas
- [ ] Variables de entorno correctas
- [ ] Callback URL accesible públicamente
- [ ] Permisos de Microsoft Graph asignados

### ❌ Conflictos de puertos
```bash
# Ver puertos en uso
sudo netstat -tlnp | grep LISTEN

# Verificar conflictos específicos
./admin-hostinger.sh conflicts
```

### ❌ SSL no funciona
- [ ] Dominio apunta correctamente al VPS
- [ ] Puerto 80 y 443 disponibles (o 8080/8443)
- [ ] Email configurado para Let's Encrypt
- [ ] Certificados generados correctamente

## 📞 Información de soporte

### 📋 Datos para soporte
```bash
# Generar información del sistema
./admin-hostinger.sh status > system-info.txt
docker --version >> system-info.txt
docker-compose --version >> system-info.txt
uname -a >> system-info.txt
```

### 🔗 URLs importantes
- **Dashboard:** `https://tu-dominio.com` o `http://IP:8502`
- **Health Check:** `http://IP:8502/_stcore/health`
- **Nginx Direct:** `http://IP:8080`
- **Admin Panel:** `./admin-hostinger.sh`

### 📝 Logs importantes
```bash
# Logs del dashboard
docker-compose -f docker-compose-hostinger.yml logs dashboard

# Logs de Nginx
docker-compose -f docker-compose-hostinger.yml logs nginx

# Logs del sistema
journalctl -u docker -f
```

## ✅ Checklist final

### 🎯 Funcionamiento completo
- [ ] Dashboard carga correctamente
- [ ] Login con Microsoft funciona
- [ ] Datos de OneDrive se muestran
- [ ] Filtros y visualizaciones funcionan
- [ ] Responsive design funciona en móvil
- [ ] Performance aceptable (< 3s carga inicial)

### 🔄 Mantenimiento configurado
- [ ] Script de administración funcionando
- [ ] Backup automático configurado
- [ ] Logs rotando correctamente
- [ ] Actualizaciones planeadas
- [ ] Monitoreo básico configurado

### 📚 Documentación
- [ ] README específico de Hostinger revisado
- [ ] Credenciales documentadas de forma segura
- [ ] Procedimientos de emergencia documentados
- [ ] Contactos de soporte identificados

---

## 🎉 ¡Despliegue completado!

Tu dashboard de gastos del hogar está ahora funcionando en tu VPS de Hostinger, compatible con tu instalación existente de N8N.

**URLs de acceso:**
- Con dominio: `https://tu-dominio.com`
- Sin dominio: `http://[IP-DE-TU-VPS]:8502`

**Administración:**
```bash
./admin-hostinger.sh
```

**Próximos pasos:**
1. Configurar backup automático
2. Configurar monitoreo
3. Documentar credenciales de forma segura
4. Planificar actualizaciones regulares
