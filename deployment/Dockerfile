# Dockerfile para producción - Dashboard de Gastos del Hogar
FROM python:3.12-slim

# Metadatos
LABEL maintainer="Tu nombre <tu-email@ejemplo.com>"
LABEL description="Dashboard de Gastos del Hogar con integración OneDrive"
LABEL version="1.1"

# Variables de entorno para optimización
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Configurar directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Crear usuario no privilegiado para seguridad
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Copiar requirements primero (para aprovechar cache de Docker)
COPY --chown=appuser:appuser requirements.txt .

# Instalar dependencias de Python
RUN pip install --user --no-cache-dir -r requirements.txt

# Agregar el directorio de pip user al PATH
ENV PATH="/home/appuser/.local/bin:${PATH}"

# Copiar archivos de la aplicación
COPY --chown=appuser:appuser dashboard_simple.py .
COPY --chown=appuser:appuser onedrive_graph.py .
COPY --chown=appuser:appuser .streamlit/ .streamlit/

# Crear directorios necesarios
RUN mkdir -p /app/data /app/logs

# Exponer puerto
EXPOSE 8501

# Variables de entorno para Streamlit
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

# Healthcheck para verificar que la app esté funcionando
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Comando para ejecutar la aplicación
CMD ["streamlit", "run", "dashboard_simple.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
