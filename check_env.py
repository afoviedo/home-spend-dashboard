import os
from dotenv import load_dotenv

# Cargar variables de entorno
print("📁 Verificando archivo .env...")
print("=" * 40)

# Verificar si existe el archivo
env_exists = os.path.exists('.env')
print(f"Archivo .env existe: {'✅ SÍ' if env_exists else '❌ NO'}")

if env_exists:
    # Cargar variables
    load_dotenv('.env')
    
    # Mostrar variables
    username = os.getenv("DASHBOARD_USERNAME")
    password_hash = os.getenv("PASSWORD_HASH")
    excel_url = os.getenv("EXCEL_URL")
    
    print(f"\n📊 Variables encontradas:")
    print(f"- DASHBOARD_USERNAME: {username}")
    print(f"- PASSWORD_HASH: {'CONFIGURADO' if password_hash else 'NO ENCONTRADO'}")
    print(f"- EXCEL_URL: {'CONFIGURADO' if excel_url else 'NO ENCONTRADO'}")
    
    if username:
        print(f"\n✅ El usuario '{username}' debería funcionar en el dashboard")
    else:
        print(f"\n❌ No se encontró usuario configurado")
else:
    print("❌ Archivo .env no encontrado en el directorio actual")
    print(f"Directorio actual: {os.getcwd()}")

print("\n🔧 Si hay problemas:")
print("1. Verifica que el archivo .env esté en el directorio del proyecto")
print("2. Reinicia el dashboard")
print("3. Usa el modo debug en el dashboard para más información")
