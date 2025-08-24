# Dashboard de Gastos del Hogar 💰

Un dashboard interactivo creado con Streamlit para analizar y visualizar gastos personales desde OneDrive con autenticación Microsoft Graph API.

## Características ✨

- 🔐 **Autenticación Microsoft Graph** - OAuth 2.0 seguro
- 📊 **Visualizaciones interactivas** con Plotly
- 🔄 **Conexión directa a OneDrive** - lee archivos Excel automáticamente
- 🎛️ **Filtros avanzados** por fecha, responsable, banco y monto
- 📱 **Diseño responsivo** que funciona en móviles y escritorio
- 📈 **Métricas en tiempo real** y tendencias
- 🚀 **Múltiples opciones de deployment** - local, VPS, Docker, Azure

## 🚀 Inicio Rápido (Desarrollo Local)

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar OAuth Microsoft Graph

1. Copia el archivo `.env.example` a `.env`:
```bash
copy .env.example .env
```

2. Configura tu aplicación en Azure Portal:
   - Ve a **App registrations** → **New registration**
   - Agrega **Redirect URI**: `http://localhost:8501/callback`
   - Copia `CLIENT_ID`, `CLIENT_SECRET`, `TENANT_ID`

3. Edita el archivo `.env` con tus datos:

```env
# URL de tu archivo Excel (debe ser accesible públicamente)
EXCEL_URL=https://tu-url-del-archivo-excel.xlsx

# Usuario para acceder al dashboard
USERNAME=admin

# Hash de la contraseña (generado con generate_password.py)
PASSWORD_HASH=$2b$12$tu_hash_de_contraseña_aqui

# Clave secreta para la sesión
SECRET_KEY=tu_clave_secreta_muy_larga_y_segura
```

### 3. Generar hash de contraseña

Ejecuta el script para generar un hash seguro de tu contraseña:

```bash
python generate_password.py
```

Copia el hash generado en tu archivo `.env`.

### 4. Configurar el archivo Excel

Tu archivo Excel debe tener las siguientes columnas en este orden:

| Columna | Descripción |
|---------|-------------|
| MessageID | ID único del mensaje |
| ID | ID de la transacción |
| Bank | Nombre del banco |
| Business | Nombre del negocio |
| Location | Ubicación de la transacción |
| Date | Fecha de la transacción |
| Card | Número/tipo de tarjeta |
| Amount | Monto de la transacción |
| Responsible | Persona responsable |

**Importante:** El archivo Excel debe estar disponible públicamente en línea (por ejemplo, en OneDrive, Google Drive, etc.) con permisos de lectura.

## Uso 📱

### Ejecutar el dashboard

```bash
streamlit run dashboard.py
```

El dashboard estará disponible en `http://localhost:8501`

### Características del Dashboard

#### 🔐 Pantalla de Login
- Ingresa tu usuario y contraseña configurados
- Autenticación segura con hash de contraseña

#### 📊 Panel Principal
- **Tarjetas de métricas:** Total de gastos, gastos del mes actual, promedio diario, número de transacciones
- **Gráfico de tendencias:** Evolución de gastos por mes
- **Gráfico circular:** Distribución de gastos por responsable
- **Gráfico de barras:** Gastos por banco y por tipo de negocio

#### 🎛️ Filtros Laterales
- **Rango de fechas:** Filtra transacciones por período
- **Responsable:** Filtra por persona específica
- **Banco:** Filtra por banco específico
- **Monto mínimo:** Filtra transacciones por monto mínimo

#### 📋 Tabla de Datos
- Vista detallada de todas las transacciones filtradas
- Ordenada por fecha (más recientes primero)
- Formato amigable de fechas y montos

## Configuración Avanzada ⚙️

### Personalizar actualización de datos

Por defecto, los datos se actualizan cada 5 minutos. Para cambiar esto, modifica el parámetro `ttl` en la función `load_data()`:

```python
@st.cache_data(ttl=300)  # 300 segundos = 5 minutos
```

### Agregar más visualizaciones

Puedes agregar nuevos gráficos modificando la función `create_charts()` en `dashboard.py`.

### Personalizar autenticación

Para agregar más usuarios, puedes modificar la función `authenticate_user()` para usar una base de datos o archivo de configuración.

## Solución de Problemas 🔧

### Error: "URL del archivo Excel no configurada"
- Verifica que la variable `EXCEL_URL` esté correctamente configurada en tu archivo `.env`

### Error: "Error al cargar los datos"
- Verifica que la URL del archivo Excel sea accesible públicamente
- Asegúrate de que el archivo tenga el formato correcto con las columnas esperadas

### Error de autenticación
- Verifica que el hash de contraseña esté correctamente generado
- Asegúrate de que el usuario y contraseña en `.env` sean correctos

### El dashboard no se actualiza
- Usa el botón "🔄 Actualizar Datos" en la barra lateral
- Verifica tu conexión a internet

## Estructura del Proyecto 📁

```
Home Spend/
├── dashboard.py          # Aplicación principal de Streamlit
├── generate_password.py  # Script para generar hash de contraseña
├── requirements.txt      # Dependencias de Python
├── .env.example         # Plantilla de variables de entorno
├── .env                 # Variables de entorno (no incluir en git)
├── .gitignore          # Archivos a ignorar en git
└── README.md           # Este archivo
```

### 3. Ejecutar localmente

```bash
# Opción 1: Script automático (Windows)
ejecutar_dashboard.bat

# Opción 2: Interfaz web
# Abrir launcher.html en el navegador

# Opción 3: Manual
streamlit run dashboard_simple.py
```

El dashboard estará disponible en `http://localhost:8501`

## � Deployment en Producción

### 🐳 Opción 1: Docker en VPS (RECOMENDADO)

La forma más fácil de hostear en tu propio servidor:

```bash
# 1. Subir proyecto al VPS
git clone https://github.com/tu-usuario/home-spend-dashboard.git
cd home-spend-dashboard/deployment

# 2. Configurar dominio
nano deploy-docker-auto.sh  # Cambiar tu-dominio.com por tu dominio real

# 3. Ejecutar instalación automática
chmod +x deploy-docker-auto.sh
./deploy-docker-auto.sh
```

**¡Eso es todo!** Tu dashboard estará en `https://tu-dominio.com` con SSL automático.

#### Administración súper fácil:
```bash
./admin.sh          # Panel de administración visual
./admin.sh status    # Ver estado
./admin.sh logs      # Ver logs
./admin.sh update    # Actualizar aplicación
./admin.sh backup    # Hacer backup
```

### 🌟 Opción 2: Azure App Service

Para deployment managed en Azure:

1. Crea App Service en Azure Portal
2. Configura deployment desde GitHub
3. Agrega variables de entorno en Azure
4. ¡Listo!

### 📖 Documentación completa de deployment:

- **🐳 Docker (súper fácil):** [`deployment/DOCKER-SIMPLE.md`](deployment/DOCKER-SIMPLE.md)
- **📋 Guía completa VPS:** [`GUIA_DEPLOYMENT_VPS.md`](GUIA_DEPLOYMENT_VPS.md)
- **🎯 Resumen ejecutivo:** [`deployment/RESUMEN-DEPLOYMENT.md`](deployment/RESUMEN-DEPLOYMENT.md)

## 📱 Funcionalidades del Dashboard

### 🔐 Autenticación Microsoft Graph
- OAuth 2.0 seguro con Microsoft
- Acceso directo a OneDrive
- Sin contraseñas que recordar

### 📊 Visualizaciones Interactivas
- **Métricas en tiempo real:** Total gastos, gastos del mes, promedio diario
- **Gráficos de tendencias:** Evolución temporal de gastos
- **Distribución circular:** Gastos por responsable
- **Análisis por categorías:** Bancos, ubicaciones, tipos de negocio

### 🎛️ Filtros Avanzados
- **Rango de fechas** personalizable
- **Responsable** específico
- **Banco** particular
- **Rango de montos**
- **Tipo de negocio**

### 📋 Vista de Datos
- Tabla detallada y filtrable
- Exportación de datos
- Ordenamiento personalizable

## ⚙️ Configuración Avanzada

### Personalizar carpeta OneDrive
```env
ONEDRIVE_FOLDER_PATH=/Casa  # Cambiar por tu carpeta
```

### Configurar entorno de producción
```env
ENVIRONMENT=production
DEBUG=false
REDIRECT_URI=https://tu-dominio.com/callback
```

## 🔒 Seguridad

### Incluida automáticamente:
- ✅ **OAuth 2.0** con Microsoft Graph
- ✅ **HTTPS obligatorio** en producción
- ✅ **Variables de entorno** para credenciales
- ✅ **Headers de seguridad** 
- ✅ **Rate limiting**
- ✅ **Firewall automático**

## 🆘 Troubleshooting

### Dashboard no carga:
```bash
# Ver logs (Docker)
./admin.sh logs

# Ver logs (local)
streamlit run dashboard_simple.py
```

### OAuth no funciona:
1. Verifica REDIRECT_URI en Azure Portal
2. Verifica variables en `.env`
3. Confirma que el dominio funcione

### Performance:
```bash
# Ver uso de recursos (Docker)
./admin.sh status
```

## 📈 Roadmap

- [ ] Dashboard de Analytics avanzado
- [ ] Alertas automáticas de gastos
- [ ] Integración con más fuentes de datos
- [ ] App móvil nativa
- [ ] Predicciones con Machine Learning

## 🤝 Contribuciones

Para contribuir al proyecto:

1. Haz fork del repositorio
2. Crea una rama para tu feature
3. Haz commit de tus cambios
4. Crea un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

---

## 🎯 Links importantes

- **📊 Dashboard en vivo:** `https://tu-dominio.com` (después del deployment)
- **📚 Documentación Docker:** [`deployment/DOCKER-SIMPLE.md`](deployment/DOCKER-SIMPLE.md)
- **🎛️ Panel de administración:** `./admin.sh` (en el servidor)
- **🔄 OAuth callback:** `https://tu-dominio.com/callback`

**¿Necesitas ayuda? ¡Abre un issue en el repositorio!** 🚀
