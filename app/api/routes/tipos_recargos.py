from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.db import models, schemas
from app.db.database import get_db

router = APIRouter()

# Ruta para leer los tipos de recargos
@router.get("/", response_model=List[schemas.TipoRecargoBase])
async def leer_tipos_recargos(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.TipoRecargo))
    return result.scalars().all()

# Ruta para leer un tipo de recargo por su ID
@router.get("/{tipo_recargo_id}", response_model=schemas.TipoRecargoBase)
async def leer_tipo_recargo(tipo_recargo_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.TipoRecargo).where(models.TipoRecargo.id == tipo_recargo_id)
    )
    tipo_recargo = result.scalar_one_or_none()
    if tipo_recargo is None:
        raise HTTPException(status_code=404, detail="Tipo de recargo no encontrado")
    return tipo_recargo

# Ruta para crear un tipo de recargo
@router.post("/", response_model=schemas.TipoRecargoBase)
async def crear_tipo_recargo(tipo_recargo: schemas.TipoRecargoCreate, db: AsyncSession = Depends(get_db)):
    db_tipo_recargo = models.TipoRecargo(**tipo_recargo.model_dump())
    db.add(db_tipo_recargo)
    await db.commit()
    await db.refresh(db_tipo_recargo)
    return db_tipo_recargo

# Ruta para actualizar un tipo de recargo
@router.put("/{tipo_recargo_id}", response_model=schemas.TipoRecargoBase)
async def actualizar_tipo_recargo(tipo_recargo_id: int, tipo_recargo: schemas.TipoRecargoCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.TipoRecargo).where(models.TipoRecargo.id == tipo_recargo_id)
    )
    db_tipo_recargo = result.scalar_one_or_none()
    if db_tipo_recargo is None:
        raise HTTPException(status_code=404, detail="Tipo de recargo no encontrado")
    for key, value in tipo_recargo.model_dump().items():
        setattr(db_tipo_recargo, key, value)
    await db.commit()
    await db.refresh(db_tipo_recargo)
    return db_tipo_recargo

# Ruta para eliminar un tipo de recargo
@router.delete("/{tipo_recargo_id}")
async def eliminar_tipo_recargo(tipo_recargo_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.TipoRecargo).where(models.TipoRecargo.id == tipo_recargo_id)
    )
    db_tipo_recargo = result.scalar_one_or_none()
    if db_tipo_recargo is None:
        raise HTTPException(status_code=404, detail="Tipo de recargo no encontrado")
    await db.delete(db_tipo_recargo)
    await db.commit()
    return {"message": "Tipo de recargo eliminado", "tipo_recargo": db_tipo_recargo}