@echo off
title Dashboard de Gastos del Hogar
echo ========================================
echo    DASHBOARD DE GASTOS DEL HOGAR
echo ========================================
echo.
echo 🚀 Iniciando dashboard...
echo.

cd /d "%~dp0"

REM Activar entorno virtual
call ".venv\Scripts\activate.bat"

REM Verificar que streamlit esté instalado
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo ❌ Error: Streamlit no está instalado
    echo 🔧 Instalando dependencias...
    pip install -r requirements.txt
)

REM Ejecutar dashboard
echo ✅ Abriendo dashboard en http://localhost:8501
echo.
echo 💡 Para detener el dashboard, presiona Ctrl+C
echo.
start http://localhost:8501
streamlit run dashboard_simple.py

pause
