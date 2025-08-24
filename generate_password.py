import bcrypt
import getpass

def generate_password_hash():
    """Genera un hash seguro para la contraseña"""
    password = getpass.getpass("Ingresa la contraseña que deseas usar: ")
    confirm_password = getpass.getpass("Confirma la contraseña: ")
    
    if password != confirm_password:
        print("❌ Las contraseñas no coinciden")
        return
    
    # Generar hash
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    print(f"\n✅ Hash generado exitosamente:")
    print(f"PASSWORD_HASH={password_hash.decode('utf-8')}")
    print(f"\nCopia este valor en tu archivo .env")

if __name__ == "__main__":
    generate_password_hash()
