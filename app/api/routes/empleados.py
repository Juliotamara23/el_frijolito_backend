from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.db import models, schemas
from app.db.database import get_db
from uuid import UUID

router = APIRouter()

# Ruta para leer todos los empleados
@router.get("/", response_model=List[schemas.Empleado])
async def leer_empleados(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Empleado))
    return result.scalars().all()

# Ruta para leer un empleado por su ID
@router.get("/{empleado_id}", response_model=schemas.Empleado)
async def leer_empleado(empleado_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Empleado).where(models.Empleado.id == empleado_id)
    )
    empleado = result.scalar_one_or_none()
    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado

# Ruta para crear un empleado
@router.post("/", status_code=201, response_model=schemas.Empleado)
async def crear_empleado(empleado: schemas.EmpleadoCreate, db: AsyncSession = Depends(get_db)):
    nuevo_empleado = models.Empleado(**empleado.model_dump())
    db.add(nuevo_empleado)
    await db.commit()
    await db.refresh(nuevo_empleado)
    return nuevo_empleado

# Ruta para actualizar un empleado
@router.put("/{empleado_id}", response_model=schemas.Empleado)
async def actualizar_empleado(empleado_id: UUID, empleado: schemas.EmpleadoUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Empleado).where(models.Empleado.id == empleado_id)
    )
    db_empleado = result.scalar_one_or_none()
    if db_empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    for key, value in empleado.model_dump(exclude_unset=True).items():
        setattr(db_empleado, key, value)
    await db.commit()
    await db.refresh(db_empleado)
    return db_empleado

# Ruta para eliminar un empleado
@router.delete("/{empleado_id}")
async def eliminar_empleado(empleado_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Empleado).where(models.Empleado.id == empleado_id)
    )
    db_empleado = result.scalar_one_or_none()
    if db_empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    await db.delete(db_empleado)
    await db.commit()
    return {"message": "Empleado eliminado exitosamente", "empleado": db_empleado}