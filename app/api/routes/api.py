from fastapi import APIRouter
from app.api.routes import empleados, nomina, config_salarios, tipos_descuentos

api_router = APIRouter()

api_router.include_router(empleados.router, prefix="/empleados", tags=["Empleados"], responses={404: {"description": "No se encontró ningun empleado"}})
api_router.include_router(nomina.router, prefix="/nominas", tags=["Nóminas"], responses={404: {"description": "No se encontró ninguna nómina"}})
api_router.include_router(config_salarios.router, prefix="/config_salarios", tags=["Configuración de Salarios"], responses={404: {"description": "No se encontró ninguna configuración de salarios"}})
api_router.include_router(tipos_descuentos.router, prefix="/tipos_descuentos", tags=["Tipos de descuentos"], responses={404: {"description": "No se encontró ningún tipo de descuento"}})