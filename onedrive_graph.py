"""
Módulo para conectar con OneDrive usando Microsoft Graph API
Requiere configuración previa en Azure Portal
"""

import msal
import requests
import streamlit as st
import os
from typing import Optional, Dict, Any
import pandas as pd
from io import BytesIO


class OneDriveGraphConnector:
    def __init__(self, client_id: str, client_secret: str, tenant_id: str):
        """
        Inicializa el conector de Microsoft Graph
        
        Args:
            client_id: Application (client) ID de Azure
            client_secret: Client secret de Azure
            tenant_id: Directory (tenant) ID de Azure
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        
        # Scopes necesarios para leer archivos
        self.scopes = ["https://graph.microsoft.com/Files.Read.All"]
        
        # URL base de Microsoft Graph
        self.graph_url = "https://graph.microsoft.com/v1.0"
        
        # Configurar MSAL
        self.app = msal.ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=f"https://login.microsoftonline.com/{self.tenant_id}"
        )
    
    def get_auth_url(self) -> str:
        """
        Genera la URL de autorización para que el usuario se autentique
        
        Returns:
            URL de autorización
        """
        redirect_uri = os.getenv('AZURE_REDIRECT_URI', 'http://localhost:8501/callback')
        auth_url = self.app.get_authorization_request_url(
            scopes=self.scopes,
            redirect_uri=redirect_uri
        )
        return auth_url
    
    def get_token_from_code(self, auth_code: str) -> Optional[Dict[str, Any]]:
        """
        Intercambia el código de autorización por un token de acceso
        
        Args:
            auth_code: Código de autorización recibido del callback
            
        Returns:
            Token de acceso o None si hay error
        """
        try:
            redirect_uri = os.getenv('AZURE_REDIRECT_URI', 'http://localhost:8501/callback')
            result = self.app.acquire_token_by_authorization_code(
                code=auth_code,
                scopes=self.scopes,
                redirect_uri=redirect_uri
            )
            
            if "access_token" in result:
                return result
            else:
                error_msg = result.get('error_description', 'Error desconocido')
                error_code = result.get('error', '')
                
                # Si el código ya fue redimido - implementar manejo según Microsoft best practices
                if "already redeemed" in error_msg or "AADSTS54005" in error_code or "AADSTS70008" in error_code:
                    # Este código ya fue usado - NO reintentarlo nunca
                    # Limpiar completamente el estado OAuth
                    _cleanup_oauth_state()
                    
                    # Limpiar parámetros de URL si aún existen
                    # Limpiar query params de forma compatible
                    if hasattr(st, 'experimental_set_query_params'):
                        st.experimental_set_query_params()
                    elif hasattr(st, 'query_params'):
                        st.query_params.clear()
                    
                    # NO redirigir automáticamente - dejar que el usuario inicie manualmente
                    st.error("⚠️ El código de autorización ya fue utilizado.")
                    st.info("🔄 Por favor, haz clic en 'Iniciar Sesión con Microsoft' para obtener un nuevo código de autorización.")
                    
                    return None
                else:
                    st.error(f"Error obteniendo token: {error_msg}")
                return None
                
        except Exception as e:
            st.error(f"Error en autenticación: {str(e)}")
            return None
    
    def get_token_from_refresh(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        Renueva el token usando el refresh token
        
        Args:
            refresh_token: Token de actualización
            
        Returns:
            Nuevo token de acceso o None si hay error
        """
        try:
            result = self.app.acquire_token_by_refresh_token(
                refresh_token=refresh_token,
                scopes=self.scopes
            )
            
            if "access_token" in result:
                return result
            else:
                st.error(f"Error renovando token: {result.get('error_description', 'Error desconocido')}")
                return None
                
        except Exception as e:
            st.error(f"Error renovando token: {str(e)}")
            return None
    
    def search_files(self, access_token: str, filename: str) -> Optional[Dict[str, Any]]:
        """
        Busca archivos por nombre en OneDrive (raíz y subdirectorios)
        
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
            # Primero intentar buscar en la raíz
            search_url = f"{self.graph_url}/me/drive/root/children"
            response = requests.get(search_url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('value'):
                # Buscar coincidencia exacta en la raíz
                for item in data['value']:
                    if item['name'].lower() == filename.lower():
                        st.success(f"✅ Archivo encontrado en raíz: {item['name']}")
                        return item
                
                # Buscar en carpetas comunes (Casa, Documents, etc.)
                common_folders = ['casa', 'documents', 'documentos', 'home', 'archivos']
                for item in data['value']:
                    if item.get('folder') and item['name'].lower() in common_folders:
                        st.info(f"🔍 Buscando en carpeta: {item['name']}")
                        folder_result = self._search_in_folder(access_token, item['id'], filename)
                        if folder_result:
                            return folder_result
            
            # Si no se encuentra en carpetas específicas, usar búsqueda global
            st.info(f"🔍 Buscando '{filename}' en todo OneDrive...")
            search_url = f"{self.graph_url}/me/drive/root/search(q='{filename.replace('.xlsx', '')}')"
            response = requests.get(search_url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('value'):
                # Buscar coincidencia exacta
                for item in data['value']:
                    if item['name'].lower() == filename.lower():
                        st.success(f"✅ Archivo encontrado: {item['name']}")
                        st.info(f"📂 Ubicación: {item.get('parentReference', {}).get('path', 'Raíz')}")
                        return item
                
                # Si no hay coincidencia exacta, buscar archivos .xlsx similares
                for item in data['value']:
                    if item['name'].lower().endswith('.xlsx') and filename.lower().replace('.xlsx', '') in item['name'].lower():
                        st.info(f"📄 Archivo similar encontrado: {item['name']}")
                        st.info(f"📂 Ubicación: {item.get('parentReference', {}).get('path', 'Raíz')}")
                        return item
            
            st.warning(f"⚠️ No se encontró el archivo: {filename}")
            return None
            
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Error buscando archivo: {str(e)}")
            return None
    
    def _search_in_folder(self, access_token: str, folder_id: str, filename: str) -> Optional[Dict[str, Any]]:
        """
        Busca un archivo en una carpeta específica
        
        Args:
            access_token: Token de acceso válido
            folder_id: ID de la carpeta donde buscar
            filename: Nombre del archivo a buscar
            
        Returns:
            Información del archivo o None si no se encuentra
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            search_url = f"{self.graph_url}/me/drive/items/{folder_id}/children"
            response = requests.get(search_url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('value'):
                for item in data['value']:
                    if item['name'].lower() == filename.lower():
                        st.success(f"✅ Archivo encontrado en carpeta: {item['name']}")
                        return item
            
            return None
            
        except requests.exceptions.RequestException as e:
            st.warning(f"⚠️ Error buscando en carpeta: {str(e)}")
            return None
    
    def download_file(self, access_token: str, file_id: str) -> Optional[bytes]:
        """
        Descarga el contenido de un archivo
        
        Args:
            access_token: Token de acceso válido
            file_id: ID del archivo en OneDrive
            
        Returns:
            Contenido del archivo en bytes o None si hay error
        """
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        download_url = f"{self.graph_url}/me/drive/items/{file_id}/content"
        
        try:
            response = requests.get(download_url, headers=headers)
            response.raise_for_status()
            
            return response.content
            
        except requests.exceptions.RequestException as e:
            st.error(f"Error descargando archivo: {str(e)}")
            return None
    
    def get_excel_data(self, access_token: str, filename: str) -> Optional[pd.DataFrame]:
        """
        Busca y descarga un archivo Excel, devolviendo un DataFrame
        
        Args:
            access_token: Token de acceso válido
            filename: Nombre del archivo Excel
            
        Returns:
            DataFrame con los datos del Excel o None si hay error
        """
        # Buscar el archivo
        file_info = self.search_files(access_token, filename)
        
        if not file_info:
            st.error(f"No se encontró el archivo: {filename}")
            return None
        
        st.success(f"✅ Archivo encontrado: {file_info['name']}")
        
        # Descargar el archivo
        file_content = self.download_file(access_token, file_info['id'])
        
        if not file_content:
            st.error("Error descargando el archivo")
            return None
        
        # Convertir a DataFrame
        try:
            df = pd.read_excel(BytesIO(file_content))
            st.success(f"✅ Archivo Excel cargado: {len(df)} filas")
            return df
            
        except Exception as e:
            st.error(f"Error leyendo Excel: {str(e)}")
            return None


def init_graph_connection() -> Optional[OneDriveGraphConnector]:
    """
    Inicializa la conexión con Microsoft Graph usando variables de entorno
    
    Returns:
        Conector configurado o None si faltan credenciales
    """
    client_id = os.getenv('AZURE_CLIENT_ID')
    client_secret = os.getenv('AZURE_CLIENT_SECRET')
    tenant_id = os.getenv('AZURE_TENANT_ID')
    
    if not all([client_id, client_secret, tenant_id]):
        st.warning("⚠️ Configuración de Azure incompleta. Revisa las variables de entorno.")
        return None
    
    return OneDriveGraphConnector(client_id, client_secret, tenant_id)


def _cleanup_oauth_state():
    """Limpia el estado de OAuth de forma segura"""
    keys_to_clean = ['processing_oauth', 'last_processed_code', 'access_token', 'refresh_token', 'authenticated']
    for key in keys_to_clean:
        if key in st.session_state:
            del st.session_state[key]
    return None

def handle_oauth_callback():
    """
    Maneja el callback de OAuth cuando el usuario regresa de Microsoft
    Implementa las mejores prácticas de Microsoft para evitar códigos reutilizados
    """
    try:
        # Usar la API compatible con versiones anteriores de Streamlit
        query_params = st.experimental_get_query_params()
        
        if 'code' in query_params:
            auth_code = query_params['code'][0] if isinstance(query_params['code'], list) else query_params['code']
            
            # Verificar si ya procesamos este código específico
            if st.session_state.get('last_processed_code') == auth_code:
                # Ya procesamos este código, retornar el token existente si lo hay
                return st.session_state.get('access_token')
            
            # Verificar si ya estamos procesando otro código
            if st.session_state.get('processing_oauth', False):
                return None
            
            # Marcar como procesando y registrar este código
            st.session_state['processing_oauth'] = True
            st.session_state['last_processed_code'] = auth_code
            
            # IMPORTANTE: Limpiar INMEDIATAMENTE los parámetros para evitar reuso
            st.experimental_set_query_params()
            
            try:
                connector = init_graph_connection()
                if not connector:
                    return _cleanup_oauth_state()
                
                # Intentar obtener el token
                token_data = connector.get_token_from_code(auth_code)
                
                if token_data and 'access_token' in token_data:
                    # Éxito - guardar tokens
                    st.session_state['access_token'] = token_data['access_token']
                    if 'refresh_token' in token_data:
                        st.session_state['refresh_token'] = token_data['refresh_token']
                    
                    st.session_state['authenticated'] = True
                    st.session_state['processing_oauth'] = False
                    
                    st.success("✅ Autenticación exitosa con Microsoft!")
                    return token_data
                else:
                    # Error al obtener token - limpiar estado
                    return _cleanup_oauth_state()
                    
            except Exception as e:
                st.error(f"Error procesando autenticación: {str(e)}")
                return _cleanup_oauth_state()
                
        elif 'error' in query_params:
            # Error de OAuth - limpiar y mostrar mensaje
            error = query_params.get('error', ['unknown_error'])
            error_desc = query_params.get('error_description', ['Error desconocido'])
            
            # Obtener el primer elemento si es lista
            error = error[0] if isinstance(error, list) else error
            error_desc = error_desc[0] if isinstance(error_desc, list) else error_desc
            
            st.experimental_set_query_params()
            st.error(f"Error de autenticación: {error_desc}")
            return None
            
    except Exception as e:
        st.error(f"Error manejando callback OAuth: {str(e)}")
        return None
    
    return None
