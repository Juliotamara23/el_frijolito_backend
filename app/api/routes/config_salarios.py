from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db import models, schemas
from app.db.database import get_db

router = APIRouter()

# Ruta para leer las configuraciones de salarios
@router.get("/", response_model=List[schemas.ConfigSalario])
def leer_config_salarios(db: Session = Depends(get_db)):
    return db.query(models.ConfigSalario).all()

# Ruta para leer una configuración de salario por su ID
@router.get("/{config_salario_id}", response_model=schemas.ConfigSalario)
def leer_config_salario(config_salario_id: int, db: Session = Depends(get_db)):
    config_salario = db.query(models.ConfigSalario).filter(models.ConfigSalario.id == config_salario_id).first()
    if config_salario is None:
        raise HTTPException(status_code=404, detail="Configuración de salario no encontrada")
    return config_salario

# Ruta para crear una configuración de salario
@router.post("/", status_code=201, response_model=schemas.ConfigSalario)
def crear_config_salario(config_salario: schemas.ConfigSalarioCreate, db: Session = Depends(get_db)):
    nueva_config_salario = models.ConfigSalario(**config_salario.model_dump())
    db.add(nueva_config_salario)
    db.commit()
    db.refresh(nueva_config_salario)
    return nueva_config_salario

# Ruta para actualizar una configuración de salario
@router.put("/{config_salario_id}", response_model=schemas.ConfigSalario)
def actualizar_config_salario(config_salario_id: int, config_salario: schemas.ConfigSalarioUpdate, db: Session = Depends(get_db)):
    db_config_salario = db.query(models.ConfigSalario).filter(models.ConfigSalario.id == config_salario_id).first()
    if db_config_salario is None:
        raise HTTPException(status_code=404, detail="Configuración de salario no encontrada")
    for key, value in config_salario.model_dump(exclude_unset=True).items():
        setattr(db_config_salario, key, value)
    db.commit()
    db.refresh(db_config_salario)
    return db_config_salario

# Ruta para eliminar una configuración de salario
@router.delete("/{config_salario_id}")
def eliminar_config_salario(config_salario_id: int, db: Session = Depends(get_db)):
    db_config_salario = db.query(models.ConfigSalario).filter(models.ConfigSalario.id == config_salario_id).first()
    if db_config_salario is None:
        raise HTTPException(status_code=404, detail="Configuración de salario no encontrada")
    db.delete(db_config_salario)
    db.commit()
    return {"message": "Configuración de salario eliminada exitosamente", "config_salario": db_config_salario}