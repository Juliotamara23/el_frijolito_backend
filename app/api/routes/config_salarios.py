from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.db import models, schemas
from app.db.database import get_db

router = APIRouter()

# Ruta para leer las configuraciones de salarios
@router.get("/", response_model=List[schemas.ConfigSalario])
async def leer_config_salarios(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.ConfigSalario))
    return result.scalars().all()

# Ruta para leer una configuración de salario por su ID
@router.get("/{config_salario_id}", response_model=schemas.ConfigSalario)
async def leer_config_salario(config_salario_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.ConfigSalario).where(models.ConfigSalario.id == config_salario_id)
    )
    config_salario = result.scalar_one_or_none()
    if config_salario is None:
        raise HTTPException(status_code=404, detail="Configuración de salario no encontrada")
    return config_salario

# Ruta para crear una configuración de salario
@router.post("/", status_code=201, response_model=schemas.ConfigSalario)
async def crear_config_salario(config_salario: schemas.ConfigSalarioCreate, db: AsyncSession = Depends(get_db)):
    nueva_config_salario = models.ConfigSalario(**config_salario.model_dump())
    db.add(nueva_config_salario)
    await db.commit()
    await db.refresh(nueva_config_salario)
    return nueva_config_salario

# Ruta para actualizar una configuración de salario
@router.put("/{config_salario_id}", response_model=schemas.ConfigSalario)
async def actualizar_config_salario(config_salario_id: int, config_salario: schemas.ConfigSalarioUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.ConfigSalario).where(models.ConfigSalario.id == config_salario_id)
    )
    db_config_salario = result.scalar_one_or_none()
    if db_config_salario is None:
        raise HTTPException(status_code=404, detail="Configuración de salario no encontrada")
    for key, value in config_salario.model_dump(exclude_unset=True).items():
        setattr(db_config_salario, key, value)
    await db.commit()
    await db.refresh(db_config_salario)
    return db_config_salario

# Ruta para eliminar una configuración de salario
@router.delete("/{config_salario_id}")
async def eliminar_config_salario(config_salario_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.ConfigSalario).where(models.ConfigSalario.id == config_salario_id)
    )
    db_config_salario = result.scalar_one_or_none()
    if db_config_salario is None:
        raise HTTPException(status_code=404, detail="Configuración de salario no encontrada")
    await db.delete(db_config_salario)
    await db.commit()
    return {"message": "Configuración de salario eliminada exitosamente", "config_salario": db_config_salario}