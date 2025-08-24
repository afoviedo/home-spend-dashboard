"""
Dashboard Simple - Versión de Diagnóstico
Test básico para verificar que Streamlit Cloud funciona
"""

import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(
    page_title="Test Dashboard",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 Dashboard de Gastos del Hogar - Test")

st.success("✅ Streamlit Cloud está funcionando correctamente!")

st.info("🔧 Versión de diagnóstico - comprobando funcionalidad básica")

# Test básico de pandas
df_test = pd.DataFrame({
    'Fecha': pd.date_range('2024-01-01', periods=5),
    'Monto': [100, 200, 150, 300, 250],
    'Categoria': ['Comida', 'Transporte', 'Salud', 'Entretenimiento', 'Comida']
})

st.subheader("📊 Test de DataFrame")
st.dataframe(df_test)

st.subheader("📈 Test de Gráfico")
st.bar_chart(df_test.set_index('Fecha')['Monto'])

# Información del entorno
st.subheader("🔍 Información del Entorno")
st.write(f"Pandas version: {pd.__version__}")
st.write(f"Streamlit version: {st.__version__}")

# Test de secrets
st.subheader("🔐 Test de Secrets")
try:
    client_id = st.secrets.get("AZURE_CLIENT_ID", "No configurado")
    st.write(f"AZURE_CLIENT_ID: {client_id[:10]}..." if len(client_id) > 10 else client_id)
    st.success("✅ Secrets accesibles")
except Exception as e:
    st.error(f"❌ Error accediendo a secrets: {e}")

st.markdown("---")
st.info("🚀 Si ves esta página, Streamlit Cloud está funcionando. El problema puede estar en la autenticación de Microsoft.")
