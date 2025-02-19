from fastapi import APIRouter
from app.api.endpoints import empleados

api_router = APIRouter()

api_router.include_router(empleados.router, prefix="/empleados", tags=["Empleados"], responses={404: {"description": "No se encontró ningun empleado"}})