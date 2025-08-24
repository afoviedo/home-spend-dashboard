# 🏠 Dashboard de Gastos del Hogar

Dashboard interactivo desarrollado con Streamlit para gestionar y visualizar gastos familiares, integrado con Microsoft OneDrive para sincronización automática de datos.

## ✨ Características

- 🔐 **Autenticación segura** con Microsoft Graph API
- 📊 **Visualizaciones interactivas** con Plotly
- 🔄 **Sincronización automática** desde OneDrive
- 📱 **Diseño responsivo** para cualquier dispositivo
- � **Filtros avanzados** por fecha, categoría y responsable
- 📈 **Métricas en tiempo real** con comparaciones
- 🤖 **Asignación inteligente** de responsables
- 💰 **Gestión automática** de gastos fijos mensuales
- 📅 **Numeración personalizada** de semanas

## 🚀 Instalación

### Prerrequisitos

- Python 3.8 o superior
- Cuenta de Microsoft con OneDrive
- Aplicación registrada en Azure Portal

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/home-spend-dashboard.git
cd home-spend-dashboard
```

### 2. Crear entorno virtual

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

1. Copia el archivo `.env.example` a `.env`:
```bash
copy .env.example .env
```

2. Edita el archivo `.env` con tus datos:

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

## Seguridad 🔒

- Las contraseñas se almacenan usando hash bcrypt
- Las variables sensibles se mantienen en archivos `.env`
- El archivo `.env` está excluido del control de versiones

## Contribuciones 🤝

Para contribuir al proyecto:

1. Haz fork del repositorio
2. Crea una rama para tu feature
3. Haz commit de tus cambios
4. Crea un Pull Request

## Licencia 📄

Este proyecto está bajo la Licencia MIT.

---

¿Necesitas ayuda? ¡Abre un issue en el repositorio!
