from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db import models, schemas
from app.db.database import get_db
from uuid import UUID

router = APIRouter()

# Ruta para leer todos los empleados
@router.get("/", response_model=List[schemas.Empleado])
def leer_empleados(db: Session = Depends(get_db)):
    return db.query(models.Empleado).all()

# Ruta para leer un empleado por su ID
@router.get("/{empleado_id}", response_model=schemas.Empleado)
def leer_empleado(empleado_id: UUID, db: Session = Depends(get_db)):
    empleado = db.query(models.Empleado).filter(models.Empleado.id == empleado_id).first()
    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado

# Ruta para crear un empleado
@router.post("/", status_code=201, response_model=schemas.Empleado)
def crear_empleado(empleado: schemas.EmpleadoCreate, db: Session = Depends(get_db)):
    nuevo_empleado = models.Empleado(**empleado.model_dump())
    db.add(nuevo_empleado)
    db.commit()
    db.refresh(nuevo_empleado)
    return nuevo_empleado

# Ruta para actualizar un empleado
@router.put("/{empleado_id}", response_model=schemas.Empleado)
def actualizar_empleado(empleado_id: UUID, empleado: schemas.EmpleadoUpdate, db: Session = Depends(get_db)):
    db_empleado = db.query(models.Empleado).filter(models.Empleado.id == empleado_id).first()
    if db_empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    for key, value in empleado.model_dump(exclude_unset=True).items():
        setattr(db_empleado, key, value)
    db.commit()
    db.refresh(db_empleado)
    return db_empleado

# Ruta para eliminar un empleado
@router.delete("/{empleado_id}")
def eliminar_empleado(empleado_id: UUID, db: Session = Depends(get_db)):
    db_empleado = db.query(models.Empleado).filter(models.Empleado.id == empleado_id).first()
    if db_empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    db.delete(db_empleado)
    db.commit()
    return {"message": "Empleado eliminado exitosamente", "empleado": db_empleado}