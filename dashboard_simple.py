"""
Dashboard de Gastos del Hogar - Versión Mejorada con Modo Demo
Streamlit app para visualizar gastos con modo demo y OneDrive
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from onedrive_graph import load_spending_data

# Configuración de la página
st.set_page_config(
    page_title="Home Spend Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .demo-banner {
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Función para generar datos demo
def generate_demo_data():
    """Genera datos de ejemplo realistas para demostración"""
    np.random.seed(42)  # Para datos consistentes
    
    # Fechas de los últimos 6 meses
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Categorías típicas de gastos del hogar
    categories = [
        'Supermercado', 'Restaurantes', 'Servicios', 'Transporte', 
        'Entretenimiento', 'Salud', 'Ropa', 'Otros'
    ]
    
    # Generar datos aleatorios pero realistas
    data = []
    for date in dates:
        # Número aleatorio de transacciones por día (0-5)
        num_transactions = np.random.poisson(2)
        
        for _ in range(num_transactions):
            category = np.random.choice(categories)
            
            # Montos realistas por categoría
            amount_ranges = {
                'Supermercado': (50, 300),
                'Restaurantes': (30, 150),
                'Servicios': (100, 500),
                'Transporte': (20, 100),
                'Entretenimiento': (25, 200),
                'Salud': (50, 400),
                'Ropa': (40, 250),
                'Otros': (10, 100)
            }
            
            min_amount, max_amount = amount_ranges[category]
            amount = np.random.uniform(min_amount, max_amount)
            
            data.append({
                'Fecha': date,
                'Categoría': category,
                'Monto': amount,
                'Descripción': f'Gasto en {category.lower()}'
            })
    
    df = pd.DataFrame(data)
    df['Mes'] = df['Fecha'].dt.to_period('M').astype(str)
    df['Semana'] = df['Fecha'].dt.to_period('W').astype(str)
    
    return df

# Función principal
def main():
    # Título principal
    st.markdown('<h1 class="main-header">🏠 Home Spend Dashboard</h1>', unsafe_allow_html=True)
    
    # Configuración de modo
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        mode = st.radio(
            "Selecciona el modo de funcionamiento:",
            ["📊 Modo Demo", "☁️ Conectar OneDrive"],
            horizontal=True
        )
    
    if mode == "📊 Modo Demo":
        st.markdown(
            '<div class="demo-banner">'
            '<h3>🎮 Modo Demo Activo</h3>'
            '<p>Usando datos de ejemplo para demostración del dashboard</p>'
            '</div>',
            unsafe_allow_html=True
        )
        df = generate_demo_data()
        
    else:  # Modo OneDrive
        st.info("☁️ **Modo OneDrive** - Conectando a tus datos reales")
        
        # Intentar cargar datos desde OneDrive
        try:
            df = load_spending_data()
            
            if df is None:
                st.warning("⚠️ No se pudieron cargar los datos de OneDrive. Cambia al Modo Demo para ver el dashboard funcionando.")
                return
                
        except Exception as e:
            st.error(f"❌ Error conectando a OneDrive: {str(e)}")
            st.info("💡 Usa el Modo Demo para ver el dashboard funcionando")
            return
    
    # Verificar que tenemos datos
    if df is None or df.empty:
        st.warning("⚠️ No hay datos disponibles")
        return
    
    # Sidebar con filtros
    st.sidebar.markdown('<p class="sidebar-header">🔧 Filtros</p>', unsafe_allow_html=True)
    
    # Filtros de fecha
    fecha_min = df['Fecha'].min().date()
    fecha_max = df['Fecha'].max().date()
    
    fecha_inicio = st.sidebar.date_input(
        "📅 Fecha inicio",
        value=fecha_min,
        min_value=fecha_min,
        max_value=fecha_max
    )
    
    fecha_fin = st.sidebar.date_input(
        "📅 Fecha fin",
        value=fecha_max,
        min_value=fecha_min,
        max_value=fecha_max
    )
    
    # Filtro de categorías
    categorias_disponibles = sorted(df['Categoría'].unique())
    categorias_seleccionadas = st.sidebar.multiselect(
        "🏷️ Categorías",
        options=categorias_disponibles,
        default=categorias_disponibles
    )
    
    # Filtro de rango de montos
    monto_min = float(df['Monto'].min())
    monto_max = float(df['Monto'].max())
    
    rango_montos = st.sidebar.slider(
        "💰 Rango de montos",
        min_value=monto_min,
        max_value=monto_max,
        value=(monto_min, monto_max),
        format="$%.0f"
    )
    
    # Aplicar filtros
    mask = (
        (df['Fecha'].dt.date >= fecha_inicio) &
        (df['Fecha'].dt.date <= fecha_fin) &
        (df['Categoría'].isin(categorias_seleccionadas)) &
        (df['Monto'] >= rango_montos[0]) &
        (df['Monto'] <= rango_montos[1])
    )
    
    df_filtrado = df[mask].copy()
    
    if df_filtrado.empty:
        st.warning("⚠️ No hay datos que coincidan con los filtros seleccionados")
        return
    
    # Métricas principales
    st.markdown("### 📊 Resumen General")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_gastos = df_filtrado['Monto'].sum()
        st.markdown(
            f'<div class="metric-container">'
            f'<h3 style="margin:0; color:#1f77b4;">💰 Total Gastos</h3>'
            f'<h2 style="margin:0;">${total_gastos:,.0f}</h2>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    with col2:
        num_transacciones = len(df_filtrado)
        st.markdown(
            f'<div class="metric-container">'
            f'<h3 style="margin:0; color:#1f77b4;">🧾 Transacciones</h3>'
            f'<h2 style="margin:0;">{num_transacciones:,}</h2>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    with col3:
        gasto_promedio = df_filtrado['Monto'].mean()
        st.markdown(
            f'<div class="metric-container">'
            f'<h3 style="margin:0; color:#1f77b4;">📈 Gasto Promedio</h3>'
            f'<h2 style="margin:0;">${gasto_promedio:,.0f}</h2>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    with col4:
        categoria_top = df_filtrado.groupby('Categoría')['Monto'].sum().idxmax()
        st.markdown(
            f'<div class="metric-container">'
            f'<h3 style="margin:0; color:#1f77b4;">🏆 Top Categoría</h3>'
            f'<h2 style="margin:0;">{categoria_top}</h2>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    # Gráficos principales
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🥧 Gastos por Categoría")
        gastos_categoria = df_filtrado.groupby('Categoría')['Monto'].sum().sort_values(ascending=False)
        
        fig_pie = px.pie(
            values=gastos_categoria.values,
            names=gastos_categoria.index,
            title="Distribución de Gastos por Categoría"
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Top 10 Categorías")
        top_categorias = gastos_categoria.head(10)
        
        fig_bar = px.bar(
            x=top_categorias.values,
            y=top_categorias.index,
            orientation='h',
            title="Gastos por Categoría (Top 10)",
            labels={'x': 'Monto ($)', 'y': 'Categoría'}
        )
        fig_bar.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Tendencias temporales
    st.markdown("### 📈 Tendencias Temporales")
    
    # Preparar datos por mes
    gastos_mes = df_filtrado.groupby('Mes')['Monto'].sum().reset_index()
    gastos_mes['Fecha_Mes'] = pd.to_datetime(gastos_mes['Mes'])
    gastos_mes = gastos_mes.sort_values('Fecha_Mes')
    
    fig_timeline = px.line(
        gastos_mes,
        x='Fecha_Mes',
        y='Monto',
        title="Evolución de Gastos Mensuales",
        labels={'Monto': 'Gasto Total ($)', 'Fecha_Mes': 'Mes'}
    )
    fig_timeline.update_traces(mode='lines+markers')
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Análisis detallado por categoría
    st.markdown("### 🔍 Análisis Detallado por Categoría")
    
    # Heatmap de gastos por categoría y mes
    pivot_data = df_filtrado.groupby(['Mes', 'Categoría'])['Monto'].sum().reset_index()
    pivot_table = pivot_data.pivot(index='Categoría', columns='Mes', values='Monto').fillna(0)
    
    fig_heatmap = px.imshow(
        pivot_table.values,
        x=pivot_table.columns,
        y=pivot_table.index,
        title="Heatmap: Gastos por Categoría y Mes",
        labels={'x': 'Mes', 'y': 'Categoría', 'color': 'Monto ($)'}
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Tabla de datos recientes
    st.markdown("### 📋 Transacciones Recientes")
    
    # Mostrar las últimas 20 transacciones
    df_recientes = df_filtrado.nlargest(20, 'Fecha')[['Fecha', 'Categoría', 'Monto', 'Descripción']]
    df_recientes['Monto'] = df_recientes['Monto'].apply(lambda x: f"${x:,.0f}")
    df_recientes['Fecha'] = df_recientes['Fecha'].dt.strftime('%Y-%m-%d')
    
    st.dataframe(
        df_recientes,
        use_container_width=True,
        hide_index=True
    )
    
    # Estadísticas adicionales
    st.markdown("### 📈 Estadísticas Adicionales")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 Estadísticas por Categoría**")
        stats_categoria = df_filtrado.groupby('Categoría')['Monto'].agg(['count', 'sum', 'mean', 'std']).round(2)
        stats_categoria.columns = ['Transacciones', 'Total ($)', 'Promedio ($)', 'Desv. Estándar ($)']
        stats_categoria = stats_categoria.sort_values('Total ($)', ascending=False)
        st.dataframe(stats_categoria, use_container_width=True)
    
    with col2:
        st.markdown("**📅 Estadísticas por Mes**")
        stats_mes = df_filtrado.groupby('Mes')['Monto'].agg(['count', 'sum', 'mean']).round(2)
        stats_mes.columns = ['Transacciones', 'Total ($)', 'Promedio ($)']
        st.dataframe(stats_mes, use_container_width=True)
    
    # Footer con información del modo
    st.markdown("---")
    mode_indicator = "🎮 Modo Demo" if mode == "📊 Modo Demo" else "☁️ Modo OneDrive"
    st.markdown(
        f"📊 Dashboard actualizado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        f"{mode_indicator} | "
        f"Mostrando {len(df_filtrado):,} transacciones de {len(df):,} totales"
    )

if __name__ == "__main__":
    main()
