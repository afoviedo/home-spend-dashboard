"""
Dashboard de Gastos del Hogar - Solo con Autenticación Microsoft
Streamlit app para visualizar gastos desde OneDrive
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import requests
from dotenv import load_dotenv
from onedrive_graph import init_graph_connection, handle_oauth_callback

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Gastos del Hogar",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar variables de entorno
load_dotenv()

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    
    .auth-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def check_microsoft_auth():
    """Verificar autenticación de Microsoft como único método de acceso"""
    
    # Manejar callback de OAuth si existe
    handle_oauth_callback()
    
    # Si ya está autenticado con Microsoft, VALIDAR que el token funcione
    if st.session_state.get('access_token'):
        # Validar que el token realmente funcione haciendo una petición simple
        connector = init_graph_connection()
        if connector:
            try:
                # Intentar hacer una petición simple para validar el token
                headers = {'Authorization': f"Bearer {st.session_state['access_token']}"}
                response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers, timeout=5)
                
                if response.status_code == 401 or response.status_code == 403:
                    # Token inválido - limpiar automáticamente y redirigir
                    st.warning("🔄 Token expirado detectado. Limpiando automáticamente...")
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.rerun()
                    
            except Exception:
                # Si hay cualquier error en la validación, limpiar
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        
        # Token válido - mostrar información del usuario en sidebar
        with st.sidebar:
            st.success(f"✅ Conectado como: {st.session_state.get('user_name', 'Usuario')}")
            if st.button("🚪 Cerrar Sesión Microsoft"):
                # Limpiar toda la sesión
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        return True
    
    # Mostrar interfaz de autenticación Microsoft
    st.markdown('<h1 class="main-header">🏠 Dashboard de Gastos del Hogar</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="auth-header">🔐 Acceso Seguro</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.info("🔐 **Autenticación con Microsoft OneDrive**")
        st.write("Para acceder a tus datos de gastos, necesitas iniciar sesión con tu cuenta de Microsoft que tiene acceso a OneDrive.")
        
        connector = init_graph_connection()
        if not connector:
            st.error("❌ Error de configuración del sistema. Contacta al administrador.")
            return False
        
        # Generar URL de autenticación
        auth_url = connector.get_auth_url()
        
        # Botón que redirige directamente a Microsoft
        st.markdown(
            f'''
            <a href="{auth_url}" target="_self">
                <button style="
                    background: linear-gradient(90deg, #1f77b4, #ff7f0e);
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 12px 24px;
                    font-size: 16px;
                    font-weight: bold;
                    width: 100%;
                    cursor: pointer;
                    text-decoration: none;
                    display: block;
                    text-align: center;
                ">
                    🚀 Iniciar Sesión con Microsoft
                </button>
            </a>
            ''',
            unsafe_allow_html=True
        )
        
        st.markdown("---")
        
        # Botón para limpiar sesión en caso de errores - MUY VISIBLE
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🧹 LIMPIAR SESIÓN Y RECONECTAR", help="Usar si hay errores de autenticación", type="secondary"):
                # Limpiar toda la sesión
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                # Limpiar parámetros de URL
                if hasattr(st, 'query_params'):
                    st.query_params.clear()
                st.success("✅ Sesión limpiada. Puedes intentar autenticarte de nuevo.")
                st.rerun()
        
        st.markdown("---")
        st.markdown("### ✨ Características del Dashboard:")
        st.markdown("- 📊 Visualización en tiempo real de tus gastos")
        st.markdown("- 📈 Gráficos interactivos y métricas")
        st.markdown("- 🔄 Datos sincronizados desde OneDrive")
        st.markdown("- 🛡️ Acceso seguro con Microsoft OAuth")
    
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
    
    # Asignar responsables basado en números de tarjeta
    if 'Card' in transformed_df.columns:
        def asignar_responsable(row):
            card = str(row.get('Card', ''))
            
            # Si ya tiene responsable asignado, mantenerlo
            responsable_actual = row.get('Responsable', '')
            if pd.notna(responsable_actual) and responsable_actual.strip():
                return responsable_actual
            
            # Asignar basado en terminación de tarjeta
            if card.endswith('9366'):
                return 'FIORELLA INFANTE AMORE'
            elif card.endswith('2081') or card.endswith('4136'):
                return 'LUIS ESTEBAN OVIEDO MATAMOROS'
            else:
                return 'ALVARO FERNANDO OVIEDO MATAMOROS'
        
        # Aplicar la función de asignación de responsables
        transformed_df['Responsable'] = transformed_df.apply(asignar_responsable, axis=1)
    elif 'Responsable' in transformed_df.columns:
        # Si no hay columna Card pero sí Responsable, completar vacíos con Alvaro
        transformed_df['Responsable'] = transformed_df['Responsable'].fillna('ALVARO FERNANDO OVIEDO MATAMOROS')
    else:
        # Si no hay columna Responsable, crearla con Alvaro por defecto
        transformed_df['Responsable'] = 'ALVARO FERNANDO OVIEDO MATAMOROS'
    
    # Filtrar filas con datos válidos
    if 'Monto' in transformed_df.columns and 'Fecha' in transformed_df.columns:
        transformed_df = transformed_df.dropna(subset=['Monto', 'Fecha'])
        transformed_df = transformed_df[transformed_df['Monto'] > 0]
    
    # Agregar gastos fijos mensuales
    transformed_df = add_monthly_fixed_expenses(transformed_df)
    
    # Completar valores vacíos con "Desconocido"
    transformed_df = transformed_df.fillna('Desconocido')
    
    return transformed_df

def add_monthly_fixed_expenses(df):
    """Agregar gastos fijos mensuales a los datos"""
    
    # Configuración de gastos fijos (fácil de modificar)
    GASTOS_FIJOS = [
        {
            'monto': 430000,
            'business': 'Arrendamiento',
            'descripcion': 'Mensualidad del Apartamento'
        },
        {
            'monto': 232000,
            'business': 'Prestamo del carro',
            'descripcion': 'Mensualidad del Carro'
        }
    ]
    
    # Configuración común para todos los gastos fijos
    RESPONSABLE_FIJO = 'ALVARO FERNANDO OVIEDO MATAMOROS'
    CARD_FIJA = '4128'
    LOCATION_FIJO = 'SAN JOSÉ'
    
    # Determinar el rango de fechas para generar gastos fijos
    fecha_inicio = pd.Timestamp('2025-01-01')
    fecha_actual = pd.Timestamp.now()
    
    # Si hay datos en el DataFrame, usar el rango de los datos existentes
    if not df.empty and 'Fecha' in df.columns:
        fecha_min_datos = df['Fecha'].min()
        fecha_max_datos = df['Fecha'].max()
        
        # Usar el rango más amplio
        fecha_inicio = min(fecha_inicio, fecha_min_datos.replace(day=1))
        fecha_actual = max(fecha_actual, fecha_max_datos)
    
    # Generar lista de primeros días de mes
    fechas_mensuales = pd.date_range(
        start=fecha_inicio,
        end=fecha_actual,
        freq='MS'  # Month Start
    )
    
    # Crear DataFrame con gastos fijos
    gastos_fijos_data = []
    
    for fecha in fechas_mensuales:
        for gasto in GASTOS_FIJOS:
            registro = {
                'MessageID': f'FIXED_{fecha.strftime("%Y%m")}_{gasto["business"].replace(" ", "_")}',
                'ID': f'FIXED{fecha.strftime("%Y%m%d")}',
                'Bank': 'Gasto Fijo',
                'Business': gasto['business'],
                'Location': LOCATION_FIJO,
                'Date': fecha,
                'Card': CARD_FIJA,
                'Amount': gasto['monto'],
                'Responsible': RESPONSABLE_FIJO,
                # Columnas transformadas
                'Categoria': gasto['business'],
                'Monto': gasto['monto'],
                'Fecha': fecha,
                'Descripcion': gasto['descripcion'],
                'Banco': 'Gasto Fijo'
            }
            gastos_fijos_data.append(registro)
    
    # Crear DataFrame de gastos fijos
    if gastos_fijos_data:
        df_gastos_fijos = pd.DataFrame(gastos_fijos_data)
        
        # Combinar con datos existentes
        if not df.empty:
            # Asegurar que las columnas coincidan
            for col in df.columns:
                if col not in df_gastos_fijos.columns:
                    df_gastos_fijos[col] = 'Gasto Fijo'
            
            for col in df_gastos_fijos.columns:
                if col not in df.columns:
                    df[col] = 'Desconocido'
            
            # Concatenar DataFrames
            df_combined = pd.concat([df, df_gastos_fijos], ignore_index=True)
        else:
            df_combined = df_gastos_fijos
        
        # Ordenar por fecha
        if 'Fecha' in df_combined.columns:
            df_combined = df_combined.sort_values('Fecha')
        
        st.info(f"✅ Agregados {len(gastos_fijos_data)} gastos fijos mensuales desde {fecha_inicio.strftime('%Y-%m-%d')}")
        
        return df_combined
    
    return df

def load_data():
    """Cargar datos desde OneDrive usando Microsoft Graph API"""
    
    connector = init_graph_connection()
    if not connector:
        st.error("❌ Error de configuración")
        return None
        
    filename = os.getenv('ONEDRIVE_FILENAME', 'HomeSpend.xlsx')
    
    try:
        df_raw = connector.get_excel_data(st.session_state['access_token'], filename)
        if df_raw is not None:
            st.success(f"✅ Datos cargados desde OneDrive: {len(df_raw)} filas")
            
            # Transformar datos al formato esperado
            df_transformed = transform_onedrive_data(df_raw)
            st.success(f"✅ Datos procesados: {len(df_transformed)} filas válidas")
            
            return df_transformed
        else:
            st.error("❌ No se pudo cargar el archivo desde OneDrive")
            return None
            
    except Exception as e:
        st.error(f"❌ Error cargando datos: {str(e)}")
        return None

def apply_filters(df):
    """Aplicar filtros globales a los datos desde el sidebar"""
    
    if df.empty:
        return df
    
    # Filtros en sidebar
    with st.sidebar:
        st.markdown("### 🔍 Filtros Globales")
        
        # Filtro por fechas
        fecha_min = df['Fecha'].min().date()
        fecha_max = df['Fecha'].max().date()
        
        fecha_inicio = st.date_input("📅 Fecha Inicio", fecha_min, key="fecha_inicio")
        fecha_fin = st.date_input("📅 Fecha Fin", fecha_max, key="fecha_fin")
        
        # Filtro por categoría
        categorias = ['Todas'] + sorted(df['Categoria'].unique().tolist())
        categoria_seleccionada = st.selectbox("🏷️ Categoría", categorias, key="categoria")
        
        # Filtro por responsable (si existe la columna)
        if 'Responsable' in df.columns:
            responsables_unicos = df['Responsable'].dropna().unique()
            if len(responsables_unicos) > 1:
                responsables = ['Todos'] + sorted(responsables_unicos.tolist())
                responsable_seleccionado = st.selectbox("👤 Responsable", responsables, key="responsable")
            else:
                responsable_seleccionado = 'Todos'
        else:
            responsable_seleccionado = 'Todos'
        
        # Aplicar filtros
        df_filtrado = df.copy()
        
        # Filtro por fechas
        df_filtrado = df_filtrado[
            (df_filtrado['Fecha'].dt.date >= fecha_inicio) & 
            (df_filtrado['Fecha'].dt.date <= fecha_fin)
        ]
        
        # Filtro por categoría
        if categoria_seleccionada != 'Todas':
            df_filtrado = df_filtrado[df_filtrado['Categoria'] == categoria_seleccionada]
        
        # Filtro por responsable
        if responsable_seleccionado != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['Responsable'] == responsable_seleccionado]
        
        # Mostrar información de filtros aplicados
        st.markdown("---")
        st.markdown("### 📊 Resumen de Filtros")
        st.info(f"📅 Período: {fecha_inicio} a {fecha_fin}")
        st.info(f"🏷️ Categoría: {categoria_seleccionada}")
        if responsable_seleccionado != 'Todos':
            st.info(f"👤 Responsable: {responsable_seleccionado}")
        st.info(f"📈 Registros: {len(df_filtrado):,} de {len(df):,}")
    
    return df_filtrado
def display_metrics(df):
    """Mostrar métricas principales"""
    
    if df.empty:
        st.warning("⚠️ No hay datos para mostrar métricas")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_gastos = df['Monto'].sum()
        st.metric(
            label="💰 Total Gastado", 
            value=f"₡{total_gastos:,.2f}"
        )
    
    with col2:
        # Gastos del período filtrado vs mes actual
        fecha_actual = datetime.now()
        gastos_mes_actual = df[df['Fecha'].dt.month == fecha_actual.month]['Monto'].sum()
        st.metric(
            label="📅 Mes Actual", 
            value=f"₡{gastos_mes_actual:,.2f}"
        )
    
    with col3:
        # Promedio diario del período filtrado
        dias_con_gastos = df['Fecha'].nunique()
        promedio_diario = total_gastos / dias_con_gastos if dias_con_gastos > 0 else 0
        st.metric(
            label="📊 Promedio Diario", 
            value=f"₡{promedio_diario:,.2f}"
        )
    
    with col4:
        # Total de transacciones filtradas
        total_transacciones = len(df)
        st.metric(
            label="🧾 Transacciones", 
            value=f"{total_transacciones:,}"
        )

def display_charts(df):
    """Mostrar gráficos con datos ya filtrados"""
    
    if df.empty:
        st.warning("⚠️ No hay datos para mostrar gráficos en el período seleccionado")
        return
    # Gráfico de línea - Tendencia de gastos con agrupación dinámica
    st.markdown("### 📈 Tendencia de Gastos")
    
    if not df.empty:
        # Selector de agrupación temporal
        col_selector, col_empty = st.columns([1, 3])
        with col_selector:
            agrupacion = st.selectbox(
                "📊 Agrupar por:",
                ["Día", "Semana ISO", "Mes"],
                key="agrupacion_tendencia"
            )
        
        # Preparar datos según la agrupación seleccionada
        df_trend = df.copy()
        
        if agrupacion == "Día":
            df_trend['Periodo'] = df_trend['Fecha'].dt.date
            titulo = "Gastos Diarios en Período Seleccionado"
            formato_fecha = "%Y-%m-%d"
        elif agrupacion == "Semana ISO":
            # Semana personalizada: S1 empieza el 1 de enero, luego lunes a domingo
            def calcular_semana_personalizada(fecha):
                # Obtener el año
                año = fecha.year
                
                # Fecha del 1 de enero del año
                primer_enero = pd.Timestamp(f'{año}-01-01')
                
                # Calcular días desde el 1 de enero
                dias_desde_enero = (fecha - primer_enero).days
                
                # La semana 1 incluye el 1 de enero hasta el primer domingo
                # Encontrar el primer domingo del año
                dias_hasta_primer_domingo = (6 - primer_enero.weekday()) % 7
                if primer_enero.weekday() == 6:  # Si el 1 de enero es domingo
                    dias_hasta_primer_domingo = 0
                
                # Calcular número de semana
                if dias_desde_enero <= dias_hasta_primer_domingo:
                    semana = 1
                else:
                    # Días después del primer domingo
                    dias_despues_primer_domingo = dias_desde_enero - dias_hasta_primer_domingo - 1
                    semana = 2 + (dias_despues_primer_domingo // 7)
                
                return f"{año}-S{semana:02d}"
            
            df_trend['Periodo'] = df_trend['Fecha'].apply(calcular_semana_personalizada)
            titulo = "Gastos por Semana (S1 desde 1 Ene, Lun-Dom) en Período Seleccionado"
            formato_fecha = "%Y-S%W"
        else:  # Mes
            df_trend['Periodo'] = df_trend['Fecha'].dt.to_period('M').astype(str)
            titulo = "Gastos Mensuales en Período Seleccionado"
            formato_fecha = "%Y-%m"
        
        # Agrupar por período
        gastos_agrupados = df_trend.groupby('Periodo')['Monto'].sum().reset_index()
        gastos_agrupados = gastos_agrupados.sort_values('Periodo')
        
        # Crear gráfico
        fig_line = px.line(
            gastos_agrupados, 
            x='Periodo', 
            y='Monto',
            title=titulo,
            labels={'Monto': 'Monto (₡)', 'Periodo': 'Período'},
            markers=True
        )
        
        # Personalizar el gráfico
        fig_line.update_layout(
            height=400,
            xaxis_tickangle=45 if agrupacion != "Día" else 0
        )
        
        # Agregar información estadística
        if len(gastos_agrupados) > 1:
            promedio = gastos_agrupados['Monto'].mean()
            maximo = gastos_agrupados['Monto'].max()
            minimo = gastos_agrupados['Monto'].min()
            
            fig_line.add_hline(
                y=promedio, 
                line_dash="dash", 
                line_color="orange",
                annotation_text=f"Promedio: ₡{promedio:,.0f}"
            )
        
        st.plotly_chart(fig_line, use_container_width=True)
        
        # Mostrar estadísticas del período
        if len(gastos_agrupados) > 1:
            col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
            
            with col_stats1:
                st.metric("📊 Promedio", f"₡{promedio:,.0f}")
            with col_stats2:
                st.metric("📈 Máximo", f"₡{maximo:,.0f}")
            with col_stats3:
                st.metric("📉 Mínimo", f"₡{minimo:,.0f}")
            with col_stats4:
                periodos_con_gastos = len(gastos_agrupados)
                st.metric(f"📅 {agrupacion}s", f"{periodos_con_gastos}")
        
    else:
        st.info("📈 No hay datos para el período seleccionado")
    
    # Gráficos en columnas
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏷️ Gastos por Categoría")
        if not df.empty:
            gastos_categoria = df.groupby('Categoria')['Monto'].sum().reset_index()
            gastos_categoria = gastos_categoria.sort_values('Monto', ascending=False)
            
            fig_bar = px.bar(
                gastos_categoria, 
                x='Categoria', 
                y='Monto',
                title="Gastos por Categoría (Período Filtrado)",
                labels={'Monto': 'Monto (₡)', 'Categoria': 'Categoría'}
            )
            fig_bar.update_layout(
                height=400,
                xaxis_tickangle=45
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("🏷️ No hay datos para mostrar")
    
    with col2:
        st.markdown("### 💰 Top 10 Gastos")
        if not df.empty:
            top_gastos = df.nlargest(10, 'Monto')[['Fecha', 'Categoria', 'Monto', 'Descripcion']]
            top_gastos['Fecha'] = top_gastos['Fecha'].dt.strftime('%Y-%m-%d')
            top_gastos['Monto'] = top_gastos['Monto'].apply(lambda x: f"₡{x:,.2f}")
            st.dataframe(top_gastos, use_container_width=True, height=400)
        else:
            st.info("💰 No hay datos para mostrar")

def show_recent_transactions(df):
    """Mostrar transacciones del período filtrado"""
    st.markdown("### 📋 Transacciones en Período Filtrado")
    
    if df.empty:
        st.info("📋 No hay transacciones para el período seleccionado")
        return
    
    # Mostrar transacciones ordenadas por fecha (más recientes primero)
    recent_df = df.sort_values('Fecha', ascending=False).head(20).copy()
    recent_df['Fecha'] = recent_df['Fecha'].dt.strftime('%Y-%m-%d %H:%M')
    recent_df['Monto'] = recent_df['Monto'].apply(lambda x: f"₡{x:,.2f}")
    
    # Seleccionar columnas a mostrar
    columns_to_show = ['Fecha', 'Categoria', 'Monto']
    if 'Descripcion' in recent_df.columns:
        columns_to_show.append('Descripcion')
    if 'Banco' in recent_df.columns:
        columns_to_show.insert(-1, 'Banco')
    if 'Responsable' in recent_df.columns:
        columns_to_show.append('Responsable')
    
    display_df = recent_df[columns_to_show]
    st.dataframe(display_df, use_container_width=True)
    
    # Mostrar información adicional
    st.caption(f"Mostrando las {len(display_df)} transacciones más recientes del período filtrado")

def main():
    """Función principal de la aplicación"""
    
    # Verificar autenticación Microsoft como única barrera
    if not check_microsoft_auth():
        return
    
    # Título principal (solo se muestra después de autenticarse)
    st.markdown('<h1 class="main-header">🏠 Dashboard de Gastos del Hogar</h1>', unsafe_allow_html=True)
    
    # Sidebar para recarga de datos
    with st.sidebar:
        st.markdown("### 🔄 Acciones")
        if st.button("🔄 Recargar Datos", use_container_width=True):
            if 'df' in st.session_state:
                del st.session_state['df']
            st.rerun()
        
        st.markdown("---")
        st.markdown("### ℹ️ Información")
        st.info(f"📅 Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Cargar datos
    if 'df' not in st.session_state:
        with st.spinner("📊 Cargando datos desde OneDrive..."):
            st.session_state['df'] = load_data()
    
    df = st.session_state['df']
    
    if df is None or df.empty:
        st.error("❌ No se pudieron cargar los datos")
        st.info("💡 Verifica que el archivo HomeSpend.xlsx existe en tu OneDrive")
        return
    
    # Aplicar filtros globales
    df_filtrado = apply_filters(df)
    
    # Mostrar métricas con datos filtrados
    display_metrics(df_filtrado)
    
    st.markdown("---")
    
    # Mostrar gráficos con datos filtrados
    display_charts(df_filtrado)
    
    st.markdown("---")
    
    # Mostrar transacciones con datos filtrados
    show_recent_transactions(df_filtrado)
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #666;">🏠 Dashboard de Gastos del Hogar - Desarrollado con Streamlit y Microsoft Graph API</p>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
