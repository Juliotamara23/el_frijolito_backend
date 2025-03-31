from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.db import models, schemas
from app.db.database import get_db
from app.db.crud import crear_reporte_nomina, actualizar_reporte_nomina, eliminar_reporte_nomina
from app.services.payroll import calcular_nomina
from app.services.reporte_payroll import obtener_reporte_nominas, obtener_reporte_nomina
from app.db.schemas import ReporteNominaResponse, ReporteNominaUpdateForm
from uuid import UUID

router = APIRouter()

# Ruta para leer todas las nóminas
@router.get("/", response_model=List[ReporteNominaResponse])
async def leer_nominas(db: AsyncSession = Depends(get_db)):
    return await obtener_reporte_nominas(db)

# Ruta para leer una nómina por su ID
@router.get("/{nomina_id}", response_model=ReporteNominaUpdateForm)
async def leer_nomina(nomina_id: UUID, db: AsyncSession = Depends(get_db)):
    nomina = await obtener_reporte_nomina(db, nomina_id)
    if nomina is None:
        raise HTTPException(status_code=404, detail="Nómina no encontrada")
    return nomina

# Ruta para crear una nómina
@router.post("/", status_code=201, response_model=schemas.ReporteNomina)
async def crear_nomina(nomina: schemas.ReporteNominaCreate, db: AsyncSession = Depends(get_db)):
    """Calcula y crea una nueva nómina"""
    # Calcular la nómina
    nomina_calculada = await calcular_nomina(db, nomina)
    # Guardar en base de datos
    return await crear_reporte_nomina(db, nomina_calculada)

# Ruta para actualizar una nómina
@router.put("/{nomina_id}", response_model=schemas.ReporteNomina)
async def actualizar_nomina(nomina_id: UUID, nomina: schemas.ReporteNominaUpdate, db: AsyncSession = Depends(get_db)):
    return await actualizar_reporte_nomina(db, nomina_id, nomina)

# Ruta para eliminar una nómina
@router.delete("/{nomina_id}")
async def eliminar_nomina(nomina_id: UUID, db: AsyncSession = Depends(get_db)):
    return await eliminar_reporte_nomina(db, nomina_id)