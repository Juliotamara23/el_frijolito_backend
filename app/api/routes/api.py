from fastapi import APIRouter
from app.api.routes import empleados, nomina, config_salarios

api_router = APIRouter()

api_router.include_router(empleados.router, prefix="/empleados", tags=["Empleados"], responses={404: {"description": "No se encontró ningun empleado"}})
api_router.include_router(nomina.router, prefix="/nominas", tags=["Nóminas"], responses={404: {"description": "No se encontró ninguna nómina"}})
api_router.include_router(config_salarios.router, prefix="/config_salarios", tags=["Salarios"], responses={404: {"description": "No se encontró ninguna configuración de salarios"}})