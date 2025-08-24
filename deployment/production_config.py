# Configuración de production para el dashboard

import os
import logging
from datetime import datetime

def setup_production_config():
    """Configurar el entorno de producción"""
    
    # Configurar logging
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    log_file = os.getenv('LOG_FILE', '/app/logs/dashboard.log')
    
    # Crear directorio de logs si no existe
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def get_environment():
    """Obtener el entorno actual"""
    return os.getenv('ENVIRONMENT', 'development')

def is_production():
    """Verificar si estamos en producción"""
    return get_environment().lower() == 'production'

def get_debug_mode():
    """Obtener el modo debug"""
    return os.getenv('DEBUG', 'true').lower() == 'true' and not is_production()

def get_redirect_uri():
    """Obtener la URI de redirección según el entorno"""
    if is_production():
        return os.getenv('REDIRECT_URI', 'https://localhost:8501/callback')
    else:
        return 'http://localhost:8501/callback'

def get_app_config():
    """Obtener configuración completa de la aplicación"""
    return {
        'environment': get_environment(),
        'debug': get_debug_mode(),
        'redirect_uri': get_redirect_uri(),
        'client_id': os.getenv('CLIENT_ID'),
        'client_secret': os.getenv('CLIENT_SECRET'),
        'tenant_id': os.getenv('TENANT_ID'),
        'onedrive_folder': os.getenv('ONEDRIVE_FOLDER_PATH', '/Casa'),
        'session_secret': os.getenv('SESSION_SECRET', 'dev-secret-key'),
    }

def validate_config():
    """Validar que todas las variables de entorno necesarias estén configuradas"""
    required_vars = ['CLIENT_ID', 'CLIENT_SECRET', 'TENANT_ID']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"Variables de entorno faltantes: {', '.join(missing_vars)}")
    
    return True
