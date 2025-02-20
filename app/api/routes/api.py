from fastapi import APIRouter
from app.api.routes import empleados, nomina

api_router = APIRouter()

api_router.include_router(empleados.router, prefix="/empleados", tags=["Empleados"], responses={404: {"description": "No se encontró ningun empleado"}})
api_router.include_router(nomina.router, prefix="/nominas", tags=["Nóminas"], responses={404: {"description": "No se encontró ninguna nómina"}})