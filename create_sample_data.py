import pandas as pd
from datetime import datetime, timedelta
import random

def create_sample_data():
    """Crea datos de ejemplo para el dashboard"""
    
    # Configuración de datos de ejemplo
    bancos = ["BAC Credomatic", "Banco Nacional", "BCR", "Banco Popular"]
    negocios = [
        "SUPER COMPRO", "AUTOMERCADO", "MAS X MENOS", "WALMART",
        "STARBUCKS", "MCDONALD'S", "PIZZA HUT", "SUBWAY",
        "GASOLINERA DELTA", "SERVICENTRO TOTAL", "BOMBA SHELL",
        "FARMACIA FISCHEL", "FARMACIA SUCRE", "CLINICA BIBLICA",
        "MULTIPLAZA", "LINCOLN PLAZA", "TERRAMALL", "CITY MALL",
        "KOLBI", "ICE", "KÖLBI TIENDA", "CLARO",
        "UBER", "UBER EATS", "RAPPI", "TAXI",
        "NETFLIX", "SPOTIFY", "AMAZON PRIME", "DISNEY+"
    ]
    
    ubicaciones = [
        "SAN JOSE, Costa Rica", "ESCAZU, Costa Rica", "SANTA ANA, Costa Rica",
        "CARTAGO, Costa Rica", "ALAJUELA, Costa Rica", "HEREDIA, Costa Rica",
        "CURRIDABAT, Costa Rica", "TIBAS, Costa Rica", "DESAMPARADOS, Costa Rica"
    ]
    
    responsables = ["ALVARO FERNANDO OVIEDO MATAMOROS", "MARIA JOSE GARCIA LOPEZ", "CARLOS ALBERTO RODRIGUEZ SOTO"]
    
    tarjetas = ["4128", "5687", "9366", "3064"]
    
    # Generar datos para los últimos 6 meses
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    data = []
    message_id = 1000
    
    for i in range(500):  # 500 transacciones de ejemplo
        # Fecha aleatoria en los últimos 6 meses
        days_ago = random.randint(0, 180)
        fecha = end_date - timedelta(days=days_ago)
        
        # Datos aleatorios
        banco = random.choice(bancos)
        negocio = random.choice(negocios)
        ubicacion = random.choice(ubicaciones)
        responsable = random.choice(responsables)
        tarjeta = random.choice(tarjetas)
        
        # Monto aleatorio (más peso a montos menores)
        if random.random() < 0.7:  # 70% montos pequeños
            monto = round(random.uniform(1000, 50000), 2)
        elif random.random() < 0.9:  # 20% montos medianos
            monto = round(random.uniform(50000, 200000), 2)
        else:  # 10% montos grandes
            monto = round(random.uniform(200000, 800000), 2)
        
        data.append({
            'MessageID': f"AQMkADAwATY0R{message_id}",
            'ID': message_id,
            'Bank': banco,
            'Business': negocio,
            'Location': ubicacion,
            'Date': fecha.strftime('%A, %B %d, %Y'),
            'Card': tarjeta,
            'Amount': f"₡{monto:,.2f}",
            'Responsible': responsable
        })
        
        message_id += 1
    
    # Crear DataFrame
    df = pd.DataFrame(data)
    
    # Guardar como Excel
    df.to_excel('datos_ejemplo.xlsx', index=False)
    print("✅ Archivo 'datos_ejemplo.xlsx' creado con 500 transacciones de ejemplo")
    print("📊 Puedes usar este archivo para probar el dashboard")
    print("🔗 Sube este archivo a OneDrive/Google Drive y usa la URL pública en la configuración")

if __name__ == "__main__":
    create_sample_data()
