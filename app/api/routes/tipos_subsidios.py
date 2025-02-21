from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.db import models, schemas
from app.db.database import get_db

router = APIRouter()

# Ruta para leer todos los tipos de subsidios
@router.get("/", response_model=List[schemas.TipoSubsidio])
async def leer_tipos_subsidios(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.TipoSubsidio))
    return result.scalars().all()

# Ruta para leer un tipo de subsidio por ID
@router.get("/{tipo_subsidio_id}", response_model=schemas.TipoSubsidio)
async def leer_tipo_subsidio(tipo_subsidio_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.TipoSubsidio).where(models.TipoSubsidio.id == tipo_subsidio_id)
    )
    tipo_subsidio = result.scalar_one_or_none()
    if tipo_subsidio is None:
        raise HTTPException(status_code=404, detail="Tipo de subsidio no encontrado")
    return tipo_subsidio

# Ruta para crear un nuevo tipo de subsidio
@router.post("/", response_model=schemas.TipoSubsidio)
async def crear_tipo_subsidio(tipo_subsidio: schemas.TipoSubsidioCreate, db: AsyncSession = Depends(get_db)):
    db_tipo_subsidio = models.TipoSubsidio(**tipo_subsidio.model_dump())
    db.add(db_tipo_subsidio)
    await db.commit()
    await db.refresh(db_tipo_subsidio)
    return db_tipo_subsidio

# Ruta para actualizar un tipo de subsidio existente
@router.put("/{tipo_subsidio_id}", response_model=schemas.TipoSubsidio)
async def actualizar_tipo_subsidio(tipo_subsidio_id: int, tipo_subsidio: schemas.TipoSubsidioCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.TipoSubsidio).where(models.TipoSubsidio.id == tipo_subsidio_id)
    )
    db_tipo_subsidio = result.scalar_one_or_none()
    if db_tipo_subsidio is None:
        raise HTTPException(status_code=404, detail="Tipo de subsidio no encontrado")
    for key, value in tipo_subsidio.model_dump().items():
        setattr(db_tipo_subsidio, key, value)
    await db.commit()
    await db.refresh(db_tipo_subsidio)
    return db_tipo_subsidio

# Ruta para eliminar un tipo de subsidio
@router.delete("/{tipo_subsidio_id}")
async def eliminar_tipo_subsidio(tipo_subsidio_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.TipoSubsidio).where(models.TipoSubsidio.id == tipo_subsidio_id)
    )
    db_tipo_subsidio = result.scalar_one_or_none()
    if db_tipo_subsidio is None:
        raise HTTPException(status_code=404, detail="Tipo de subsidio no encontrado")
    await db.delete(db_tipo_subsidio)
    await db.commit()
    return {"message": "Tipo de subsidio eliminado", "tipo_subsidio": db_tipo_subsidio}