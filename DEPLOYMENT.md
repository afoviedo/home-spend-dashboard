# Instrucciones para configurar Azure para Streamlit Cloud

## 📋 Configuración de Azure App Registration

### 1. Ve a Azure Portal
- URL: https://portal.azure.com
- Navega a: "App registrations"
- Busca tu app: "Home Spend Dashboard"

### 2. Actualizar Redirect URIs
En "Authentication" > "Platform configurations" > "Web":

**URLs a agregar:**
```
http://localhost:8501/callback
http://localhost:8502/callback
http://localhost:8503/callback
https://tu-app-name.streamlit.app/callback
```

⚠️ **IMPORTANTE**: Reemplaza "tu-app-name" con el nombre real que elijas en Streamlit Cloud

### 3. Verificar permisos API
En "API permissions" debe tener:
- Microsoft Graph > Files.Read (Delegated)
- Status: ✅ Granted for [Tu organización]

### 4. Notas importantes
- La URL de Streamlit Cloud será algo como: https://afoviedo-home-dashboard.streamlit.app
- Debes agregar esta URL + "/callback" a Azure ANTES del primer deploy
- Si no lo haces, la autenticación fallará

### 5. Opcional: Dominio personalizado
Streamlit Cloud permite dominios personalizados en planes pagos si quieres usar tu propio dominio más adelante.
