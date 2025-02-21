from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db import models, schemas
from app.db.database import get_db

router = APIRouter()

# Ruta para leer los tipos de recargos
@router.get("/", response_model=List[schemas.TipoRecargoBase])
def read_tipos_recargos(db: Session = Depends(get_db)):
    tipos_recargos = db.query(models.TipoRecargo).all()
    return tipos_recargos

# Ruta para leer un tipo de recargo por su ID
@router.get("/{tipo_recargo_id}", response_model=schemas.TipoRecargoBase)
def read_tipo_recargo(tipo_recargo_id: int, db: Session = Depends(get_db)):
    tipo_recargo = db.query(models.TipoRecargo).filter(models.TipoRecargo.id == tipo_recargo_id).first()
    if tipo_recargo is None:
        raise HTTPException(status_code=404, detail="Tipo de recargo no encontrado")
    return tipo_recargo

# Ruta para crear un tipo de recargo
@router.post("/", response_model=schemas.TipoRecargoBase)
def create_tipo_recargo(tipo_recargo: schemas.TipoRecargoCreate, db: Session = Depends(get_db)):
    db_tipo_recargo = models.TipoRecargo(**tipo_recargo.model_dump())
    db.add(db_tipo_recargo)
    db.commit()
    db.refresh(db_tipo_recargo)
    return db_tipo_recargo

# Ruta para actualizar un tipo de recargo
@router.put("/{tipo_recargo_id}", response_model=schemas.TipoRecargoBase)
def update_tipo_recargo(tipo_recargo_id: int, tipo_recargo: schemas.TipoRecargoCreate, db: Session = Depends(get_db)):
    db_tipo_recargo = db.query(models.TipoRecargo).filter(models.TipoRecargo.id == tipo_recargo_id).first()
    if db_tipo_recargo is None:
        raise HTTPException(status_code=404, detail="Tipo de recargo no encontrado")
    for key, value in tipo_recargo.model_dump().items():
        setattr(db_tipo_recargo, key, value)
    db.commit()
    db.refresh(db_tipo_recargo)
    return db_tipo_recargo

# Ruta para eliminar un tipo de recargo
@router.delete("/{tipo_recargo_id}")
def delete_tipo_recargo(tipo_recargo_id: int, db: Session = Depends(get_db)):
    db_tipo_recargo = db.query(models.TipoRecargo).filter(models.TipoRecargo.id == tipo_recargo_id).first()
    if db_tipo_recargo is None:
        raise HTTPException(status_code=404, detail="Tipo de recargo no encontrado")
    db.delete(db_tipo_recargo)
    db.commit()
    return {"message": "Tipo de recargo eliminado", "tipo_recargo": db_tipo_recargo}