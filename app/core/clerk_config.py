import os
from dotenv import load_dotenv
from clerk_sdk.clerk import Clerk
from clerk_sdk.resources.users import Users
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

# Cargar variables de entorno
load_dotenv()

# Obtener la clave secreta de Clerk
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")

if not CLERK_SECRET_KEY:
    raise ValueError("CLERK_SECRET_KEY no está configurada en las variables de entorno.")

# Inicializar el cliente de Clerk SDK
clerk = Clerk(secret_key=CLERK_SECRET_KEY)

# Esquema de seguridad para extraer el token Bearer
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependencia de FastAPI para autenticar al usuario usando un token de Clerk.
    Verifica el token JWT y devuelve el objeto de usuario de Clerk si es válido.
    """
    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticación no proporcionado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Verifica el token usando la clave secreta de Clerk.
        # Clerk SDK puede manejar la verificación de firma, caducidad, etc.
        # Usa la clave pública JWKS de Clerk para la verificación real de tokens de sesión.
        # Clerk SDK internamente descarga y usa las JWKS para esto.
        # La clave secreta CLERK_SECRET_KEY es para operaciones de backend-a-Clerk.
        # Para la verificación de tokens JWT de sesión (Bearer Token), clerk_sdk.Clerk
        # ya viene con la lógica para usar las claves públicas de Clerk.
        
        # Opcional: Puedes loguear el token para depuración
        # print(f"Token recibido: {token}")

        # La función `clerk.verify_token` es el método asíncrono para verificar tokens de sesión.
        # Este método validará la firma, la fecha de expiración, y otros claims estándar.
        decoded_token = await clerk.verify_token(token)

        # Puedes acceder a los claims del token decodificado
        user_id = decoded_token.get('sub') # 'sub' es el user ID en los claims estándar de JWT
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: user_id (sub) no encontrado",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Opcional: Obtener detalles completos del usuario desde Clerk si es necesario
        # Esto es útil si necesitas datos que no están en el token (ej. custom attributes)
        # user_data = await clerk.users.get_user(user_id)
        # return user_data # Podrías devolver el objeto User de Clerk

        # Por ahora, simplemente devolveremos el token decodificado
        # o el user_id para indicar que la autenticación fue exitosa.
        return {"user_id": user_id, "token_claims": decoded_token}

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        print(f"Error inesperado durante la verificación del token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al procesar la autenticación",
        )