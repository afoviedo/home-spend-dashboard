import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import bcrypt
import requests
from io import BytesIO

# Cargar variables de entorno de forma explícita
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

# Verificar que las variables se cargaron correctamente
if not os.getenv("DASHBOARD_USERNAME"):
    st.error("❌ No se pudo cargar el archivo .env. Verifica que existe en el directorio del proyecto.")

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Gastos del Hogar",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Funciones de autenticación
def check_password(password, hashed_password):
    """Verifica la contraseña contra el hash"""
    try:
        if not password or not hashed_password:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        st.error(f"Error en la verificación de contraseña: {e}")
        return False

def authenticate_user(username, password):
    """Autentica al usuario"""
    try:
        correct_username = os.getenv("DASHBOARD_USERNAME", "admin")
        stored_password_hash = os.getenv("PASSWORD_HASH")
        
        # Debug info (solo para desarrollo)
        if st.session_state.get('debug_mode', False):
            st.write(f"Debug - Usuario esperado: {correct_username}")
            st.write(f"Debug - Usuario ingresado: {username}")
            st.write(f"Debug - Hash configurado: {bool(stored_password_hash)}")
        
        if not stored_password_hash:
            st.error("❌ Configuración de contraseña no encontrada en .env")
            return False
            
        if username == correct_username and stored_password_hash:
            return check_password(password, stored_password_hash)
        return False
    except Exception as e:
        st.error(f"Error en la autenticación: {e}")
        return False

def login_form():
    """Formulario de login"""
    st.title("🔐 Acceso al Dashboard de Gastos")
    st.markdown("---")
    
    # Obtener usuario configurado
    configured_user = os.getenv("DASHBOARD_USERNAME", "admin")
    
    # Mostrar información de configuración
    st.info(f"👤 Usuario configurado: **{configured_user}**")
    
    # Verificar archivo .env
    env_exists = os.path.exists('.env')
    st.info(f"📁 Archivo .env encontrado: **{'✅ SÍ' if env_exists else '❌ NO'}**")
    
    # Opción de debug
    debug_mode = st.checkbox("🔧 Modo debug (mostrar información técnica)", key="debug_checkbox")
    if debug_mode:
        st.session_state['debug_mode'] = True
        # Mostrar información técnica
        st.code(f"""
Variables de entorno detectadas:
- DASHBOARD_USERNAME: {os.getenv("DASHBOARD_USERNAME", "NO ENCONTRADO")}
- PASSWORD_HASH: {'CONFIGURADO' if os.getenv("PASSWORD_HASH") else 'NO ENCONTRADO'}
- EXCEL_URL: {'CONFIGURADO' if os.getenv("EXCEL_URL") else 'NO ENCONTRADO'}
- Directorio actual: {os.getcwd()}
- Archivo .env existe: {os.path.exists('.env')}
        """)
    
    with st.form("login_form"):
        username = st.text_input("Usuario", value=configured_user)
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Ingresar")
        
        if submitted:
            if authenticate_user(username, password):
                st.session_state['authenticated'] = True
                st.session_state['username'] = username
                st.success("✅ Autenticación exitosa")
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos")
                st.warning("💡 Si el problema persiste, verifica la configuración con: `python test_password.py`")

@st.cache_data(ttl=300)  # Cache por 5 minutos
def load_data():
    """Carga los datos desde el archivo Excel en línea o local"""
    try:
        excel_url = os.getenv("EXCEL_URL")
        if not excel_url:
            st.error("URL del archivo Excel no configurada")
            return None
        
        # Opción 1: Intentar cargar desde URL
        if excel_url.startswith('http'):
            st.info(f"📥 Intentando descargar desde: {excel_url[:50]}...")
            
            # Convertir URL de OneDrive a formato de descarga directa si es necesario
            if "1drv.ms" in excel_url or "onedrive.live.com" in excel_url:
                if "?e=" in excel_url:
                    excel_url = excel_url.replace("?e=", "&download=1&e=")
                else:
                    excel_url += "&download=1"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            try:
                response = requests.get(excel_url, headers=headers, timeout=30)
                response.raise_for_status()
                
                # Verificar que se descargó contenido válido
                if len(response.content) == 0:
                    raise Exception("El archivo descargado está vacío")
                
                # Verificar si es HTML (página web) en lugar de Excel
                content_type = response.headers.get('content-type', '').lower()
                if 'text/html' in content_type:
                    raise Exception("OneDrive devolvió una página web en lugar del archivo Excel")
                
                # Intentar leer el archivo Excel
                try:
                    df = pd.read_excel(BytesIO(response.content), engine='openpyxl')
                except Exception:
                    df = pd.read_excel(BytesIO(response.content), engine='xlrd')
                
                st.success(f"✅ Datos cargados desde URL: {len(df)} filas")
                
            except Exception as url_error:
                st.warning(f"⚠️ Error al cargar desde URL: {str(url_error)}")
                st.info("🔄 Intentando cargar datos de ejemplo local...")
                
                # Fallback: cargar datos de ejemplo
                if os.path.exists('datos_ejemplo.xlsx'):
                    df = pd.read_excel('datos_ejemplo.xlsx')
                    st.warning("📊 Usando datos de ejemplo locales. Para usar datos reales, configura correctamente la URL de OneDrive.")
                else:
                    st.error("❌ No se encontraron datos de ejemplo. Ejecuta: python create_sample_data.py")
                    return None
        
        # Opción 2: Archivo local
        else:
            if os.path.exists(excel_url):
                df = pd.read_excel(excel_url)
                st.success(f"✅ Datos cargados desde archivo local: {len(df)} filas")
            else:
                st.error(f"❌ Archivo local no encontrado: {excel_url}")
                return None
        
        # Verificar que el DataFrame no esté vacío
        if df.empty:
            st.error("❌ El archivo está vacío")
            return None
        
        # Mostrar información de debug si está habilitado
        if st.session_state.get('debug_mode', False):
            st.write(f"**Columnas encontradas:** {list(df.columns)}")
            st.write(f"**Primeras filas:**")
            st.dataframe(df.head(3))
        
        # Verificar y ajustar columnas
        expected_columns = 9
        if len(df.columns) < expected_columns:
            st.error(f"❌ El archivo debe tener al menos {expected_columns} columnas. Se encontraron {len(df.columns)}.")
            return None
        
        # Asignar nombres de columnas (tomar solo las primeras 9)
        df = df.iloc[:, :9]  # Tomar solo las primeras 9 columnas
        df.columns = ['MessageID', 'ID', 'Bank', 'Business', 'Location', 'Date', 'Card', 'Amount', 'Responsible']
        
        # Convertir la fecha
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Convertir el monto a numérico
        df['Amount'] = pd.to_numeric(df['Amount'].astype(str).str.replace(',', ''), errors='coerce')
        
        # Filtrar filas válidas
        df = df.dropna(subset=['Date', 'Amount'])
        
        return df
        
    except Exception as e:
        st.error(f"Error al cargar los datos: {str(e)}")
        return None

def create_summary_cards(df):
    """Crea tarjetas de resumen"""
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Filtros para el mes actual
    current_month_data = df[
        (df['Date'].dt.month == current_month) & 
        (df['Date'].dt.year == current_year)
    ]
    
    # Métricas
    total_gastos = df['Amount'].sum()
    gastos_mes_actual = current_month_data['Amount'].sum()
    promedio_diario = current_month_data['Amount'].sum() / max(current_month_data['Date'].dt.day.max(), 1)
    num_transacciones = len(current_month_data)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 Total Gastos",
            value=f"₡{total_gastos:,.2f}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="📅 Gastos Mes Actual",
            value=f"₡{gastos_mes_actual:,.2f}",
            delta=None
        )
    
    with col3:
        st.metric(
            label="📊 Promedio Diario",
            value=f"₡{promedio_diario:,.2f}",
            delta=None
        )
    
    with col4:
        st.metric(
            label="🧾 Transacciones del Mes",
            value=f"{num_transacciones}",
            delta=None
        )

def create_charts(df):
    """Crea los gráficos del dashboard"""
    
    # Gráfico de gastos por mes
    st.subheader("📈 Tendencia de Gastos Mensuales")
    
    monthly_data = df.groupby([df['Date'].dt.to_period('M')])['Amount'].sum().reset_index()
    monthly_data['Date'] = monthly_data['Date'].dt.to_timestamp()
    
    fig_monthly = px.line(
        monthly_data, 
        x='Date', 
        y='Amount',
        title='Gastos por Mes',
        labels={'Amount': 'Monto (₡)', 'Date': 'Fecha'}
    )
    fig_monthly.update_traces(line_color='#1f77b4', line_width=3)
    st.plotly_chart(fig_monthly, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico por responsable
        st.subheader("👤 Gastos por Responsable")
        responsible_data = df.groupby('Responsible')['Amount'].sum().reset_index()
        responsible_data = responsible_data.sort_values('Amount', ascending=False)
        
        fig_responsible = px.pie(
            responsible_data,
            values='Amount',
            names='Responsible',
            title='Distribución de Gastos por Responsable'
        )
        st.plotly_chart(fig_responsible, use_container_width=True)
    
    with col2:
        # Gráfico por banco/tarjeta
        st.subheader("🏦 Gastos por Banco")
        bank_data = df.groupby('Bank')['Amount'].sum().reset_index()
        bank_data = bank_data.sort_values('Amount', ascending=False).head(10)
        
        fig_bank = px.bar(
            bank_data,
            x='Amount',
            y='Bank',
            orientation='h',
            title='Top 10 Bancos por Monto de Gastos'
        )
        st.plotly_chart(fig_bank, use_container_width=True)
    
    # Gráfico de gastos por categoría de negocio
    st.subheader("🏪 Gastos por Tipo de Negocio")
    business_data = df.groupby('Business')['Amount'].sum().reset_index()
    business_data = business_data.sort_values('Amount', ascending=False).head(15)
    
    fig_business = px.bar(
        business_data,
        x='Business',
        y='Amount',
        title='Top 15 Negocios por Monto de Gastos'
    )
    fig_business.update_xaxis(tickangle=45)
    st.plotly_chart(fig_business, use_container_width=True)

def create_filters(df):
    """Crea los filtros laterales"""
    st.sidebar.header("🎛️ Filtros")
    
    # Filtro de fecha
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    
    date_range = st.sidebar.date_input(
        "Rango de Fechas",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Filtro de responsable
    responsables = ['Todos'] + list(df['Responsible'].dropna().unique())
    selected_responsible = st.sidebar.selectbox("Responsable", responsables)
    
    # Filtro de banco
    bancos = ['Todos'] + list(df['Bank'].dropna().unique())
    selected_bank = st.sidebar.selectbox("Banco", bancos)
    
    # Filtro de monto mínimo
    min_amount = st.sidebar.number_input("Monto Mínimo (₡)", min_value=0.0, value=0.0)
    
    return date_range, selected_responsible, selected_bank, min_amount

def filter_data(df, date_range, responsible, bank, min_amount):
    """Aplica los filtros a los datos"""
    filtered_df = df.copy()
    
    # Filtro de fecha
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df['Date'].dt.date >= start_date) &
            (filtered_df['Date'].dt.date <= end_date)
        ]
    
    # Filtro de responsable
    if responsible != 'Todos':
        filtered_df = filtered_df[filtered_df['Responsible'] == responsible]
    
    # Filtro de banco
    if bank != 'Todos':
        filtered_df = filtered_df[filtered_df['Bank'] == bank]
    
    # Filtro de monto
    filtered_df = filtered_df[filtered_df['Amount'] >= min_amount]
    
    return filtered_df

def show_data_table(df):
    """Muestra la tabla de datos"""
    st.subheader("📋 Datos Detallados")
    
    # Ordenar por fecha descendente
    df_display = df.sort_values('Date', ascending=False)
    
    # Formatear la tabla
    df_display['Date'] = df_display['Date'].dt.strftime('%Y-%m-%d')
    df_display['Amount'] = df_display['Amount'].apply(lambda x: f"₡{x:,.2f}")
    
    st.dataframe(
        df_display[['Date', 'Business', 'Location', 'Amount', 'Responsible', 'Bank']],
        use_container_width=True,
        hide_index=True
    )

def main():
    """Función principal"""
    
    # Verificar autenticación
    if 'authenticated' not in st.session_state or not st.session_state['authenticated']:
        login_form()
        return
    
    # Header del dashboard
    st.title("💰 Dashboard de Gastos del Hogar")
    st.markdown(f"Bienvenido, **{st.session_state.get('username', 'Usuario')}**")
    
    # Botón de logout
    if st.sidebar.button("🚪 Cerrar Sesión"):
        st.session_state['authenticated'] = False
        st.rerun()
    
    # Botón para actualizar datos
    if st.sidebar.button("🔄 Actualizar Datos"):
        st.cache_data.clear()
        st.rerun()
    
    # Cargar datos
    with st.spinner("Cargando datos..."):
        df = load_data()
    
    if df is None or df.empty:
        st.error("No se pudieron cargar los datos")
        return
    
    # Crear filtros
    date_range, responsible, bank, min_amount = create_filters(df)
    
    # Aplicar filtros
    filtered_df = filter_data(df, date_range, responsible, bank, min_amount)
    
    if filtered_df.empty:
        st.warning("No hay datos que coincidan con los filtros seleccionados")
        return
    
    # Mostrar información de datos filtrados
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Registros mostrados:** {len(filtered_df)}")
    st.sidebar.markdown(f"**Total general:** {len(df)}")
    
    # Crear tarjetas de resumen
    create_summary_cards(filtered_df)
    
    st.markdown("---")
    
    # Crear gráficos
    create_charts(filtered_df)
    
    st.markdown("---")
    
    # Mostrar tabla de datos
    show_data_table(filtered_df)
    
    # Footer
    st.markdown("---")
    st.markdown("*Dashboard actualizado automáticamente cada 5 minutos*")

if __name__ == "__main__":
    main()
