"""
Dashboard de Gastos del Hogar con integración Microsoft Graph
Autor: GitHub Copilot
Fecha: 2025-08-24
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import bcrypt
import os
from dotenv import load_dotenv
from onedrive_graph import init_graph_connection, handle_oauth_callback

# Cargar variables de entorno
load_dotenv()

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Gastos del Hogar",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .stAlert {
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def check_password():
    """Verificar credenciales de usuario"""
    def verify_credentials(username, password):
        stored_username = os.getenv('DASHBOARD_USERNAME')
        stored_password_hash = os.getenv('PASSWORD_HASH')
        
        if stored_username and stored_password_hash:
            if username == stored_username:
                return bcrypt.checkpw(password.encode('utf-8'), stored_password_hash.encode('utf-8'))
        return False

    # Si ya está autenticado, mostrar opción de logout
    if st.session_state.get('authenticated', False):
        with st.sidebar:
            st.success(f"✅ Conectado como: {st.session_state.get('username', 'Usuario')}")
            if st.button("🚪 Cerrar Sesión"):
                # Limpiar toda la sesión
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        return True

    # Formulario de login
    st.markdown('<h1 class="main-header">🏠 Dashboard de Gastos del Hogar</h1>', unsafe_allow_html=True)
    
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                st.markdown("### 🔐 Iniciar Sesión")
                username = st.text_input("👤 Usuario")
                password = st.text_input("🔑 Contraseña", type="password")
                submit_button = st.form_submit_button("Ingresar", use_container_width=True)
                
                if submit_button:
                    if verify_credentials(username, password):
                        st.session_state['authenticated'] = True
                        st.session_state['username'] = username
                        st.success("✅ ¡Bienvenido!")
                        st.rerun()
                    else:
                        st.error("❌ Usuario o contraseña incorrectos")
    
    return False

def transform_onedrive_data(df):
    """Transformar datos de OneDrive a formato esperado del dashboard"""
    if df is None or df.empty:
        return df
    
    # Mapear columnas de OneDrive a formato esperado
    column_mapping = {
        'Amount': 'Monto',
        'Business': 'Categoria', 
        'Date': 'Fecha',
        'Location': 'Descripcion',
        'Bank': 'Banco',
        'Responsible': 'Responsable'
    }
    
    # Crear DataFrame transformado
    transformed_df = df.copy()
    
    # Renombrar columnas si existen
    for old_col, new_col in column_mapping.items():
        if old_col in transformed_df.columns:
            transformed_df = transformed_df.rename(columns={old_col: new_col})
    
    # Procesar columna de monto
    if 'Monto' in transformed_df.columns:
        # Limpiar el formato de moneda (remover ₡, comas, etc.)
        transformed_df['Monto'] = transformed_df['Monto'].astype(str)
        transformed_df['Monto'] = transformed_df['Monto'].str.replace('₡', '', regex=False)
        transformed_df['Monto'] = transformed_df['Monto'].str.replace(',', '', regex=False)
        transformed_df['Monto'] = pd.to_numeric(transformed_df['Monto'], errors='coerce')
        transformed_df['Monto'] = transformed_df['Monto'].abs()  # Valores absolutos para gastos
    
    # Procesar columna de fecha
    if 'Fecha' in transformed_df.columns:
        transformed_df['Fecha'] = pd.to_datetime(transformed_df['Fecha'], errors='coerce')
    
    # Limpiar valores nulos en categoría
    if 'Categoria' in transformed_df.columns:
        transformed_df['Categoria'] = transformed_df['Categoria'].fillna('Otros')
    
    # Filtrar filas con datos válidos
    if 'Monto' in transformed_df.columns and 'Fecha' in transformed_df.columns:
        transformed_df = transformed_df.dropna(subset=['Monto', 'Fecha'])
        transformed_df = transformed_df[transformed_df['Monto'] > 0]
    
    return transformed_df

def load_data():
    """Cargar datos desde OneDrive usando Microsoft Graph API o archivo local como respaldo"""
    
    # Verificar si hay autenticación de Microsoft Graph
    if 'access_token' in st.session_state:
        connector = init_graph_connection()
        if connector:
            filename = os.getenv('ONEDRIVE_FILENAME', 'HomeSpend.xlsx')
            
            try:
                df_raw = connector.get_excel_data(st.session_state['access_token'], filename)
                if df_raw is not None:
                    st.success(f"✅ Datos cargados desde OneDrive: {len(df_raw)} filas")
                    
                    # Mostrar estructura de datos para debug
                    with st.expander("🔍 Estructura de datos cargados"):
                        st.write("Columnas encontradas:", list(df_raw.columns))
                        st.write("Primeras 3 filas:", df_raw.head(3))
                    
                    # Transformar datos al formato esperado
                    df_transformed = transform_onedrive_data(df_raw)
                    st.success(f"✅ Datos transformados: {len(df_transformed)} filas válidas")
                    
                    return df_transformed
                else:
                    st.warning("⚠️ No se pudo cargar desde OneDrive, usando datos locales")
            except Exception as e:
                st.warning(f"⚠️ Error con OneDrive: {str(e)}, usando datos locales")
    
    # Cargar desde archivo local como respaldo
    excel_url = os.getenv('EXCEL_URL', 'datos_ejemplo.xlsx')
    
    try:
        # Intentar cargar archivo local
        if os.path.exists(excel_url):
            df = pd.read_excel(excel_url)
            st.info("📁 Datos cargados desde archivo local")
            return df
        else:
            st.error(f"❌ No se encontró el archivo: {excel_url}")
            return create_sample_data()
    except Exception as e:
        st.error(f"❌ Error cargando datos: {str(e)}")
        return create_sample_data()

def create_sample_data():
    """Crear datos de ejemplo si no se puede cargar el archivo"""
    st.info("📊 Generando datos de ejemplo...")
    
    fechas = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    
    categorias = ['Alimentación', 'Transporte', 'Entretenimiento', 'Servicios', 'Salud', 'Educación', 'Otros']
    
    data = []
    for fecha in fechas:
        if pd.np.random.rand() > 0.7:  # 30% probabilidad de gasto por día
            categoria = pd.np.random.choice(categorias)
            if categoria == 'Alimentación':
                monto = pd.np.random.uniform(10, 150)
            elif categoria == 'Transporte':
                monto = pd.np.random.uniform(5, 50)
            elif categoria == 'Servicios':
                monto = pd.np.random.uniform(50, 300)
            else:
                monto = pd.np.random.uniform(10, 200)
            
            data.append({
                'Fecha': fecha,
                'Categoria': categoria,
                'Monto': round(monto, 2),
                'Descripcion': f'Gasto en {categoria.lower()}'
            })
    
    return pd.DataFrame(data)

def setup_onedrive_auth():
    """Configurar autenticación con OneDrive usando Microsoft Graph"""
    
    st.markdown("### 🔗 Conectar con OneDrive")
    
    # Verificar configuración de Azure
    connector = init_graph_connection()
    if not connector:
        st.error("❌ Configuración de Azure incompleta")
        with st.expander("📋 Instrucciones de configuración"):
            st.markdown("""
            Para conectar con OneDrive necesitas:
            
            1. **Registrar una aplicación en Azure Portal**
            2. **Agregar las credenciales al archivo .env**:
               - `AZURE_CLIENT_ID`
               - `AZURE_CLIENT_SECRET` 
               - `AZURE_TENANT_ID`
               - `ONEDRIVE_FILENAME` (nombre de tu archivo Excel)
            
            ¿Ya completaste el registro en Azure Portal?
            """)
        return
    
    # Manejar callback de OAuth primero
    if 'code' in st.query_params:
        result = handle_oauth_callback()
        if result:
            st.rerun()
        return
    
    # Verificar si ya está autenticado
    if 'access_token' in st.session_state:
        st.success("✅ Conectado a OneDrive")
        if st.button("🔄 Renovar conexión"):
            if 'refresh_token' in st.session_state:
                new_token = connector.get_token_from_refresh(st.session_state['refresh_token'])
                if new_token:
                    st.session_state['access_token'] = new_token['access_token']
                    st.success("✅ Token renovado")
                    st.rerun()
        return
    
    # Mostrar botón de autenticación
    st.info("🔐 Necesitas autenticarte con Microsoft para acceder a OneDrive")
    
    if st.button("🚀 Conectar con OneDrive", use_container_width=True):
        auth_url = connector.get_auth_url()
        st.markdown(f"👆 [**Haz clic aquí para autenticarte con Microsoft**]({auth_url})")
        st.info("Después de autenticarte, serás redirigido de vuelta a esta aplicación.")

def display_metrics(df):
    """Mostrar métricas principales"""
    
    if df.empty:
        st.warning("⚠️ No hay datos para mostrar métricas")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_gastos = df['Monto'].sum()
        unique_days = len(df.groupby('Fecha'))
        avg_daily = total_gastos / unique_days if unique_days > 0 else 0
        st.metric(
            label="💰 Total Gastado", 
            value=f"${total_gastos:,.2f}",
            delta=f"Promedio diario: ${avg_daily:,.2f}"
        )
    
    with col2:
        gastos_mes = df[df['Fecha'].dt.month == datetime.now().month]['Monto'].sum()
        st.metric(
            label="📅 Este Mes", 
            value=f"${gastos_mes:,.2f}",
            delta="Mes actual"
        )
    
    with col3:
        categoria_gastos = df.groupby('Categoria')['Monto'].sum()
        if not categoria_gastos.empty:
            categoria_top = categoria_gastos.idxmax()
            monto_top = categoria_gastos.max()
            st.metric(
                label="🏆 Mayor Categoría", 
                value=categoria_top,
                delta=f"${monto_top:,.2f}"
            )
        else:
            st.metric(
                label="🏆 Mayor Categoría", 
                value="N/A",
                delta="Sin datos"
            )
    
    with col4:
        fecha_limite = datetime.now() - timedelta(days=7)
        gastos_semana = df[df['Fecha'] >= fecha_limite]['Monto'].sum()
        st.metric(
            label="📊 Última Semana", 
            value=f"${gastos_semana:,.2f}",
            delta="7 días"
        )

def create_charts(df):
    """Crear gráficos de análisis"""
    
    if df.empty:
        st.warning("⚠️ No hay datos para mostrar gráficos")
        return
    
    # Gráfico de gastos por categoría
    st.markdown("### 📊 Gastos por Categoría")
    gastos_categoria = df.groupby('Categoria')['Monto'].sum().reset_index()
    
    if not gastos_categoria.empty:
        fig_pie = px.pie(
            gastos_categoria, 
            values='Monto', 
            names='Categoria',
            title="Distribución de Gastos por Categoría",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("📊 No hay datos suficientes para el gráfico de categorías")
    
    # Gráfico de tendencia temporal
    st.markdown("### 📈 Tendencia de Gastos")
    gastos_diarios = df.groupby('Fecha')['Monto'].sum().reset_index()
    
    if not gastos_diarios.empty:
        fig_line = px.line(
            gastos_diarios, 
            x='Fecha', 
            y='Monto',
            title="Gastos Diarios a lo Largo del Tiempo",
            markers=True
        )
        fig_line.update_layout(height=400)
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("📈 No hay datos suficientes para el gráfico de tendencias")
    
    # Gráfico de barras por mes
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Gastos Mensuales")
        df['Mes'] = df['Fecha'].dt.strftime('%Y-%m')
        gastos_mensuales = df.groupby('Mes')['Monto'].sum().reset_index()
        
        if not gastos_mensuales.empty:
            fig_bar = px.bar(
                gastos_mensuales, 
                x='Mes', 
                y='Monto',
                title="Gastos por Mes",
                color='Monto',
                color_continuous_scale='Blues'
            )
            fig_bar.update_layout(height=400)
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("📊 No hay datos suficientes para gastos mensuales")
    
    with col2:
        st.markdown("### 🎯 Top 10 Gastos")
        if len(df) >= 10:
            top_gastos = df.nlargest(10, 'Monto')[['Fecha', 'Categoria', 'Monto', 'Descripcion']]
        else:
            top_gastos = df[['Fecha', 'Categoria', 'Monto', 'Descripcion']].sort_values('Monto', ascending=False)
        
        if not top_gastos.empty:
            st.dataframe(top_gastos, use_container_width=True, height=400)
        else:
            st.info("🎯 No hay datos para mostrar")

def main():
    """Función principal de la aplicación"""
    
    # Verificar autenticación
    if not check_password():
        return
    
    # Título principal
    st.markdown('<h1 class="main-header">🏠 Dashboard de Gastos del Hogar</h1>', unsafe_allow_html=True)
    
    # Sidebar para configuración
    with st.sidebar:
        st.markdown("### ⚙️ Configuración")
        
        # Sección de OneDrive
        setup_onedrive_auth()
        
        st.markdown("---")
        
        # Información del sistema
        st.markdown("### ℹ️ Información")
        st.info(f"📅 Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        if st.button("🔄 Recargar Datos"):
            if 'df' in st.session_state:
                del st.session_state['df']
            st.rerun()
    
    # Cargar datos
    if 'df' not in st.session_state:
        with st.spinner("📊 Cargando datos..."):
            st.session_state['df'] = load_data()
    
    df = st.session_state['df']
    
    if df is None or df.empty:
        st.error("❌ No se pudieron cargar los datos")
        st.info("💡 Verifica que el archivo Excel exista y tenga datos válidos")
        return
    
    # Procesar datos
    # Verificar y ajustar nombres de columnas
    if 'Fecha' not in df.columns:
        # Buscar columnas que puedan ser fechas
        date_columns = [col for col in df.columns if any(word in col.lower() for word in ['fecha', 'date', 'time', 'día', 'dia'])]
        if date_columns:
            df = df.rename(columns={date_columns[0]: 'Fecha'})
        else:
            st.error("❌ No se encontró una columna de fecha en los datos")
            return
    
    if 'Monto' not in df.columns:
        # Buscar columnas que puedan ser montos
        amount_columns = [col for col in df.columns if any(word in col.lower() for word in ['monto', 'amount', 'precio', 'cost', 'gasto', 'valor'])]
        if amount_columns:
            df = df.rename(columns={amount_columns[0]: 'Monto'})
        else:
            st.error("❌ No se encontró una columna de monto en los datos")
            return
    
    if 'Categoria' not in df.columns:
        # Buscar columnas que puedan ser categorías
        category_columns = [col for col in df.columns if any(word in col.lower() for word in ['categoria', 'category', 'tipo', 'type', 'class'])]
        if category_columns:
            df = df.rename(columns={category_columns[0]: 'Categoria'})
        else:
            # Si no hay categoría, crear una genérica
            df['Categoria'] = 'General'
    
    if 'Descripcion' not in df.columns:
        # Buscar columnas que puedan ser descripciones
        desc_columns = [col for col in df.columns if any(word in col.lower() for word in ['descripcion', 'description', 'detalle', 'detail', 'concepto'])]
        if desc_columns:
            df = df.rename(columns={desc_columns[0]: 'Descripcion'})
        else:
            # Si no hay descripción, crear una genérica
            df['Descripcion'] = 'Gasto general'
    
    # Convertir tipos de datos
    try:
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce')
        # Eliminar filas con montos inválidos
        df = df.dropna(subset=['Monto'])
    except Exception as e:
        st.error(f"❌ Error procesando datos: {str(e)}")
        return
    
    # Mostrar métricas
    display_metrics(df)
    
    st.markdown("---")
    
    # Crear gráficos
    create_charts(df)
    
    # Tabla de datos recientes
    st.markdown("### 📋 Gastos Recientes")
    datos_recientes = df.sort_values('Fecha', ascending=False).head(20)
    st.dataframe(datos_recientes, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "💡 Dashboard de Gastos del Hogar - Desarrollado con Streamlit y Microsoft Graph API"
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
