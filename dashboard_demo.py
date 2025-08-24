import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import bcrypt

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Gastos del Hogar - DEMO",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Funciones de autenticación (simplificadas para demo)
def authenticate_user(username, password):
    """Autentica al usuario - Demo mode"""
    return username == "demo" and password == "demo123"

def login_form():
    """Formulario de login - Demo mode"""
    st.title("🔐 Demo - Dashboard de Gastos")
    st.info("**Usuario demo:** demo | **Contraseña:** demo123")
    st.markdown("---")
    
    with st.form("login_form"):
        username = st.text_input("Usuario", value="demo")
        password = st.text_input("Contraseña", type="password", value="demo123")
        submitted = st.form_submit_button("Ingresar")
        
        if submitted:
            if authenticate_user(username, password):
                st.session_state['authenticated'] = True
                st.session_state['username'] = username
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos")

@st.cache_data(ttl=300)
def load_demo_data():
    """Carga los datos desde el archivo Excel local"""
    try:
        df = pd.read_excel('datos_ejemplo.xlsx')
        
        # Limpiar y procesar los datos
        df.columns = ['MessageID', 'ID', 'Bank', 'Business', 'Location', 'Date', 'Card', 'Amount', 'Responsible']
        
        # Convertir la fecha
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Limpiar el monto (remover ₡ y comas)
        df['Amount'] = df['Amount'].astype(str).str.replace('₡', '').str.replace(',', '')
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
        
        # Filtrar filas válidas
        df = df.dropna(subset=['Date', 'Amount'])
        
        return df
        
    except Exception as e:
        st.error(f"Error al cargar los datos: {str(e)}")
        st.error("Asegúrate de que el archivo 'datos_ejemplo.xlsx' esté en el directorio del proyecto")
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
    promedio_diario = current_month_data['Amount'].sum() / max(current_month_data['Date'].dt.day.max(), 1) if len(current_month_data) > 0 else 0
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
            title='Top Bancos por Monto de Gastos',
            labels={'Amount': 'Monto (₡)', 'Bank': 'Banco'}
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
        title='Top 15 Negocios por Monto de Gastos',
        labels={'Amount': 'Monto (₡)', 'Business': 'Negocio'}
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
    df_display['Amount_formatted'] = df_display['Amount'].apply(lambda x: f"₡{x:,.2f}")
    
    st.dataframe(
        df_display[['Date', 'Business', 'Location', 'Amount_formatted', 'Responsible', 'Bank']].rename(columns={'Amount_formatted': 'Amount'}),
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
    st.title("💰 Dashboard de Gastos del Hogar - DEMO")
    st.markdown(f"Bienvenido, **{st.session_state.get('username', 'Usuario')}**")
    st.info("🚀 Esta es una versión demo con datos de ejemplo. Para usar con datos reales, configura `dashboard.py`")
    
    # Botón de logout
    if st.sidebar.button("🚪 Cerrar Sesión"):
        st.session_state['authenticated'] = False
        st.rerun()
    
    # Botón para actualizar datos
    if st.sidebar.button("🔄 Actualizar Datos"):
        st.cache_data.clear()
        st.rerun()
    
    # Cargar datos
    with st.spinner("Cargando datos de ejemplo..."):
        df = load_demo_data()
    
    if df is None or df.empty:
        st.error("No se pudieron cargar los datos de ejemplo")
        st.info("Ejecuta `python create_sample_data.py` para generar los datos de ejemplo")
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
    st.markdown("*Dashboard Demo - Datos de ejemplo generados automáticamente*")

if __name__ == "__main__":
    main()
