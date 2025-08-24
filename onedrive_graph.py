"""
Módulo para conectar con OneDrive usando Microsoft Graph API
Utiliza device code flow para compatibilidad con Streamlit Cloud
"""

import msal
import requests
import streamlit as st
import os
from typing import Optional, Dict, Any
import pandas as pd
from io import BytesIO
import time


class OneDriveGraphConnector:
    def __init__(self, client_id: str, tenant_id: str):
        """
        Inicializa el conector de Microsoft Graph
        
        Args:
            client_id: Application (client) ID de Azure
            tenant_id: Directory (tenant) ID de Azure
        """
        self.client_id = client_id
        self.tenant_id = tenant_id
        
        # Scopes necesarios para leer archivos
        self.scopes = ["https://graph.microsoft.com/Files.Read.All"]
        
        # URL base de Microsoft Graph
        self.graph_url = "https://graph.microsoft.com/v1.0"
        
        # Configurar MSAL para device code flow (más compatible con Streamlit)
        self.app = msal.PublicClientApplication(
            client_id=self.client_id,
            authority=f"https://login.microsoftonline.com/{self.tenant_id}"
        )
    
    def authenticate_device_flow(self):
        """
        Autentica usando device code flow - versión simplificada
        """
        # Verificar si ya hay un token válido en session_state
        if "access_token" in st.session_state:
            return st.session_state["access_token"]
        
        # Inicializar o recuperar el flow del session_state
        if "device_flow" not in st.session_state:
            # Iniciar device flow
            try:
                flow = self.app.initiate_device_flow(scopes=self.scopes)
                
                if "user_code" not in flow:
                    st.error("❌ Error: No se pudo iniciar el flujo de autenticación")
                    return None
                
                st.session_state["device_flow"] = flow
            except Exception as e:
                st.error(f"❌ Error iniciando autenticación: {str(e)}")
                return None
        else:
            flow = st.session_state["device_flow"]
        
        # Mostrar instrucciones al usuario
        st.info(f"""
        🔐 **Autenticación requerida**
        
        1. Ve a: **{flow['verification_uri']}**
        2. Ingresa el código: **{flow['user_code']}**
        3. Inicia sesión con tu cuenta Microsoft
        4. Regresa aquí y haz clic en "Verificar Autenticación"
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Botón para verificar si la autenticación se completó
            if st.button("🔄 Verificar Autenticación"):
                with st.spinner("🔍 Verificando autenticación..."):
                    try:
                        # Intentar obtener token con timeout corto
                        result = self.app.acquire_token_by_device_flow(flow)
                        
                        if "access_token" in result:
                            st.session_state["access_token"] = result["access_token"]
                            # Limpiar el flow del session_state
                            if "device_flow" in st.session_state:
                                del st.session_state["device_flow"]
                            st.success("✅ ¡Autenticación exitosa!")
                            st.rerun()
                            return result["access_token"]
                        elif result.get("error") == "authorization_pending":
                            st.warning("⏳ Aún no has completado la autenticación. Completa el proceso en Microsoft y vuelve a intentar.")
                            return None
                        else:
                            st.error(f"❌ Error de autenticación: {result.get('error_description', 'Error desconocido')}")
                            # Limpiar flow en caso de error
                            if "device_flow" in st.session_state:
                                del st.session_state["device_flow"]
                            return None
                    except Exception as e:
                        st.error(f"❌ Error inesperado: {str(e)}")
                        # Limpiar flow en caso de error
                        if "device_flow" in st.session_state:
                            del st.session_state["device_flow"]
                        return None
        
        with col2:
            # Botón para reiniciar el proceso
            if st.button("🔄 Generar Nuevo Código"):
                if "device_flow" in st.session_state:
                    del st.session_state["device_flow"]
                st.rerun()
        
        return None
    
    def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información del usuario autenticado
        
        Args:
            access_token: Token de acceso válido
            
        Returns:
            Información del usuario o None si hay error
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(f"{self.graph_url}/me", headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error obteniendo información del usuario: {str(e)}")
            return None
    
    def search_files(self, access_token: str, filename: str) -> Optional[Dict[str, Any]]:
        """
        Busca archivos por nombre en OneDrive
        
        Args:
            access_token: Token de acceso válido
            filename: Nombre del archivo a buscar
            
        Returns:
            Información del archivo o None si no se encuentra
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            # Buscar archivo por nombre
            search_url = f"{self.graph_url}/me/drive/search(q='{filename}')"
            response = requests.get(search_url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            files = data.get('value', [])
            
            if files:
                # Filtrar archivos exactos (no parciales)
                exact_matches = [f for f in files if f['name'].lower() == filename.lower()]
                if exact_matches:
                    return exact_matches[0]
                else:
                    return files[0]  # Fallback al primer resultado
            
            return None
            
        except requests.exceptions.RequestException as e:
            st.error(f"Error buscando archivo: {str(e)}")
            return None
    
    def download_file(self, access_token: str, file_id: str) -> Optional[bytes]:
        """
        Descarga un archivo de OneDrive
        
        Args:
            access_token: Token de acceso válido
            file_id: ID del archivo a descargar
            
        Returns:
            Contenido del archivo en bytes o None si hay error
        """
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        try:
            download_url = f"{self.graph_url}/me/drive/items/{file_id}/content"
            response = requests.get(download_url, headers=headers)
            response.raise_for_status()
            
            return response.content
            
        except requests.exceptions.RequestException as e:
            st.error(f"Error descargando archivo: {str(e)}")
            return None
    
    def load_excel_from_onedrive(self, access_token: str, filename: str) -> Optional[pd.DataFrame]:
        """
        Carga un archivo Excel desde OneDrive como DataFrame
        
        Args:
            access_token: Token de acceso válido
            filename: Nombre del archivo Excel
            
        Returns:
            DataFrame con los datos o None si hay error
        """
        try:
            # Buscar archivo
            file_info = self.search_files(access_token, filename)
            if not file_info:
                st.error(f"❌ Archivo '{filename}' no encontrado en OneDrive")
                return None
            
            # Descargar archivo
            file_content = self.download_file(access_token, file_info['id'])
            if not file_content:
                st.error(f"❌ Error descargando '{filename}'")
                return None
            
            # Leer Excel con motor específico y manejo robusto de errores
            df = None
            
            # Determinar el engine basado en la extensión del archivo
            file_extension = filename.lower().split('.')[-1]
            
            if file_extension in ['xlsx', 'xlsm']:
                # Para archivos .xlsx y .xlsm usar openpyxl
                try:
                    df = pd.read_excel(BytesIO(file_content), engine='openpyxl')
                    st.success(f"✅ Archivo '{filename}' cargado con openpyxl")
                except Exception as e:
                    st.warning(f"⚠️ Error con openpyxl: {str(e)}")
                    
            elif file_extension == 'xls':
                # Para archivos .xls usar xlrd
                try:
                    df = pd.read_excel(BytesIO(file_content), engine='xlrd')
                    st.success(f"✅ Archivo '{filename}' cargado con xlrd")
                except Exception as e:
                    st.warning(f"⚠️ Error con xlrd: {str(e)}")
            
            # Si no se pudo cargar con el engine específico, intentar otros métodos
            if df is None:
                engines_to_try = ['openpyxl', 'xlrd', 'calamine']
                
                for engine in engines_to_try:
                    try:
                        df = pd.read_excel(BytesIO(file_content), engine=engine)
                        st.success(f"✅ Archivo '{filename}' cargado exitosamente con {engine} ({len(df)} filas)")
                        break
                    except Exception as e:
                        st.warning(f"⚠️ Falló {engine}: {str(e)}")
                        continue
                
                # Último intento sin especificar engine
                if df is None:
                    try:
                        df = pd.read_excel(BytesIO(file_content))
                        st.success(f"✅ Archivo '{filename}' cargado con engine por defecto ({len(df)} filas)")
                    except Exception as e:
                        st.error(f"❌ Error final procesando Excel: {str(e)}")
                        return None
            
            return df
            
        except Exception as e:
            st.error(f"❌ Error general procesando archivo Excel: {str(e)}")
            return None


def init_graph_connection() -> Optional[OneDriveGraphConnector]:
    """
    Inicializa la conexión con Microsoft Graph usando variables de entorno
    
    Returns:
        Conector configurado o None si faltan credenciales
    """
    # Intentar leer desde secrets primero (Streamlit Cloud)
    try:
        client_id = st.secrets["AZURE_CLIENT_ID"]
        tenant_id = st.secrets["AZURE_TENANT_ID"]
        # Si llegamos aquí, estamos en Streamlit Cloud
        st.info("🌐 Ejecutándose en Streamlit Cloud")
    except:
        # Fallback para desarrollo local
        client_id = os.getenv('AZURE_CLIENT_ID')
        tenant_id = os.getenv('AZURE_TENANT_ID')
        st.info("💻 Ejecutándose en entorno local")
    
    if not all([client_id, tenant_id]):
        st.warning("⚠️ Configuración de Azure incompleta. Revisa las variables de entorno.")
        return None
    
    return OneDriveGraphConnector(client_id, tenant_id)


def load_spending_data() -> Optional[pd.DataFrame]:
    """
    Función principal para cargar datos de gastos desde OneDrive
    
    Returns:
        DataFrame con datos de gastos o None si hay error
    """
    # Inicializar conexión
    connector = init_graph_connection()
    if not connector:
        return None
    
    # Autenticar usuario
    access_token = connector.authenticate_device_flow()
    if not access_token:
        st.warning("🔑 Necesitas autenticarte para acceder a tus datos de OneDrive")
        return None
    
    # Obtener nombre del archivo desde configuración
    try:
        filename = st.secrets.get("ONEDRIVE_FILENAME", "HomeSpend.xlsx")
    except:
        filename = os.getenv("ONEDRIVE_FILENAME", "HomeSpend.xlsx")
    
    # Cargar datos
    return connector.load_excel_from_onedrive(access_token, filename)
