"""
Dashboard de Gastos del Hogar - Con Device Flow Authentication
Streamlit app para visualizar gastos desde OneDrive
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from onedrive_graph import load_spending_data

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
        text-align: center;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3em;
        font-weight: bold;
        margin-bottom: 0.5em;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .category-chip {
        display: inline-block;
        background: #f0f2f6;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        margin: 0.25rem;
        font-size: 0.8rem;
    }
    .sidebar .element-container iframe {
        background-color: transparent;
    }
    .stSelectbox label {
        font-weight: bold;
        color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

def format_currency(amount):
    """Formatear cantidad como moneda colombiana"""
    if pd.isna(amount):
        return "$0"
    return f"${amount:,.0f}"

def create_monthly_spending_chart(df):
    """Crear gráfico de gastos mensuales"""
    if df.empty:
        return go.Figure()
    
    monthly_data = df.groupby([df['Fecha'].dt.to_period('M')])['Monto'].sum().reset_index()
    monthly_data['Fecha_str'] = monthly_data['Fecha'].astype(str)
    
    fig = px.line(
        monthly_data, 
        x='Fecha_str', 
        y='Monto',
        title='📈 Tendencia de Gastos Mensuales',
        labels={'Fecha_str': 'Mes', 'Monto': 'Gasto Total'},
        markers=True
    )
    
    fig.update_layout(
        xaxis_title="Mes",
        yaxis_title="Gasto Total",
        hovermode='x unified'
    )
    
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>Gasto: %{y:,.0f}<extra></extra>',
        line=dict(width=3),
        marker=dict(size=8)
    )
    
    return fig

def create_category_chart(df):
    """Crear gráfico de gastos por categoría"""
    if df.empty:
        return go.Figure()
    
    category_data = df.groupby('Categoría')['Monto'].sum().sort_values(ascending=True)
    
    fig = px.bar(
        x=category_data.values,
        y=category_data.index,
        orientation='h',
        title='💰 Gastos por Categoría',
        labels={'x': 'Gasto Total', 'y': 'Categoría'},
        color=category_data.values,
        color_continuous_scale='viridis'
    )
    
    fig.update_layout(
        showlegend=False,
        yaxis={'categoryorder': 'total ascending'}
    )
    
    fig.update_traces(
        hovertemplate='<b>%{y}</b><br>Gasto: %{x:,.0f}<extra></extra>'
    )
    
    return fig

def create_daily_spending_chart(df):
    """Crear gráfico de gastos diarios del último mes"""
    if df.empty:
        return go.Figure()
    
    # Filtrar último mes
    last_month = df['Fecha'].max() - pd.DateOffset(months=1)
    recent_df = df[df['Fecha'] >= last_month]
    
    daily_data = recent_df.groupby('Fecha')['Monto'].sum().reset_index()
    
    fig = px.scatter(
        daily_data,
        x='Fecha',
        y='Monto',
        title='📅 Gastos Diarios (Último Mes)',
        labels={'Fecha': 'Fecha', 'Monto': 'Gasto Diario'},
        size='Monto',
        hover_data={'Monto': ':,.0f'}
    )
    
    # Añadir línea de tendencia
    fig.add_scatter(
        x=daily_data['Fecha'],
        y=daily_data['Monto'].rolling(window=7, center=True).mean(),
        mode='lines',
        name='Promedio móvil 7 días',
        line=dict(color='red', width=2, dash='dash')
    )
    
    fig.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Gasto Diario"
    )
    
    return fig

def show_metrics(df):
    """Mostrar métricas principales"""
    if df.empty:
        st.warning("No hay datos para mostrar métricas")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_spent = df['Monto'].sum()
        st.metric("💰 Gasto Total", format_currency(total_spent))
    
    with col2:
        avg_monthly = df.groupby(df['Fecha'].dt.to_period('M'))['Monto'].sum().mean()
        st.metric("📅 Promedio Mensual", format_currency(avg_monthly))
    
    with col3:
        current_month = df[df['Fecha'].dt.to_period('M') == df['Fecha'].max().to_period('M')]['Monto'].sum()
        st.metric("📈 Mes Actual", format_currency(current_month))
    
    with col4:
        num_transactions = len(df)
        st.metric("🔢 Transacciones", f"{num_transactions:,}")

def show_dashboard(df):
    """Mostrar el dashboard principal"""
    if df.empty:
        st.warning("📊 No hay datos disponibles para mostrar")
        return
    
    # Sidebar para filtros
    with st.sidebar:
        st.header("🔧 Filtros")
        
        # Filtro de fechas
        min_date = df['Fecha'].min().date()
        max_date = df['Fecha'].max().date()
        
        date_range = st.date_input(
            "📅 Rango de fechas",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        # Filtro de categorías
        categories = ["Todas"] + sorted(df['Categoría'].unique().tolist())
        selected_category = st.selectbox("🏷️ Categoría", categories)
        
        # Filtro de monto mínimo
        min_amount = st.number_input(
            "💵 Monto mínimo",
            min_value=0,
            value=0,
            step=10000
        )
        
        # Botón para limpiar token (cerrar sesión)
        if st.button("🚪 Cerrar Sesión"):
            if "access_token" in st.session_state:
                del st.session_state["access_token"]
            st.rerun()
    
    # Aplicar filtros
    filtered_df = df.copy()
    
    # Filtro de fechas
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df['Fecha'].dt.date >= start_date) & 
            (filtered_df['Fecha'].dt.date <= end_date)
        ]
    
    # Filtro de categoría
    if selected_category != "Todas":
        filtered_df = filtered_df[filtered_df['Categoría'] == selected_category]
    
    # Filtro de monto
    filtered_df = filtered_df[filtered_df['Monto'] >= min_amount]
    
    # Mostrar métricas
    show_metrics(filtered_df)
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_monthly_spending_chart(filtered_df), use_container_width=True)
        st.plotly_chart(create_daily_spending_chart(filtered_df), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_category_chart(filtered_df), use_container_width=True)
        
        # Top 10 gastos
        st.subheader("🔝 Top 10 Gastos")
        top_expenses = filtered_df.nlargest(10, 'Monto')[['Fecha', 'Descripción', 'Categoría', 'Monto']]
        top_expenses['Monto'] = top_expenses['Monto'].apply(format_currency)
        st.dataframe(top_expenses, use_container_width=True, hide_index=True)
    
    # Tabla de datos completa
    with st.expander("📋 Ver todos los datos"):
        display_df = filtered_df.copy()
        display_df['Monto'] = display_df['Monto'].apply(format_currency)
        st.dataframe(display_df, use_container_width=True, hide_index=True)

def main():
    """Función principal de la aplicación"""
    
    # Título principal
    st.markdown('<h1 class="main-header">🏠 Dashboard de Gastos del Hogar</h1>', unsafe_allow_html=True)
    
    # Cargar datos con autenticación integrada
    with st.spinner("🔄 Cargando datos de OneDrive..."):
        df = load_spending_data()
    
    if df is None:
        st.stop()  # La función load_spending_data ya maneja la UI de autenticación
    
    # Continuar con el dashboard si los datos se cargaron exitosamente
    show_dashboard(df)

if __name__ == "__main__":
    main()
