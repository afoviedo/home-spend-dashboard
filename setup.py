import os
import bcrypt
import secrets

def setup_dashboard():
    """Configuración inicial del dashboard"""
    print("🚀 Configuración del Dashboard de Gastos del Hogar")
    print("=" * 50)
    
    # Verificar si .env ya existe
    env_file = ".env"
    if os.path.exists(env_file):
        overwrite = input("⚠️  El archivo .env ya existe. ¿Sobrescribir? (s/N): ").lower()
        if overwrite != 's':
            print("❌ Configuración cancelada")
            return
    
    # Obtener URL del Excel
    print("\n📊 Configuración del archivo Excel")
    excel_url = input("Ingresa la URL de tu archivo Excel: ").strip()
    
    if not excel_url:
        print("❌ URL del Excel es requerida")
        return
    
    # Configurar usuario
    print("\n👤 Configuración de usuario")
    username = input("Ingresa el nombre de usuario (default: admin): ").strip()
    if not username:
        username = "admin"
    
    # Configurar contraseña
    import getpass
    password = getpass.getpass("Ingresa la contraseña: ")
    confirm_password = getpass.getpass("Confirma la contraseña: ")
    
    if password != confirm_password:
        print("❌ Las contraseñas no coinciden")
        return
    
    # Generar hash de contraseña
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    # Generar clave secreta
    secret_key = secrets.token_urlsafe(32)
    
    # Crear archivo .env
    env_content = f"""# Variables de entorno para el dashboard
EXCEL_URL={excel_url}
DASHBOARD_USERNAME={username}
PASSWORD_HASH={password_hash.decode('utf-8')}
SECRET_KEY={secret_key}
"""
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("\n✅ Configuración completada exitosamente!")
    print(f"📁 Archivo .env creado")
    print(f"👤 Usuario: {username}")
    print(f"🔗 URL Excel: {excel_url}")
    
    print("\n🚀 Para ejecutar el dashboard:")
    print("streamlit run dashboard.py")

if __name__ == "__main__":
    setup_dashboard()
