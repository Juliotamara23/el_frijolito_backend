from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db import models, schemas
from app.db.database import get_db

router = APIRouter()

# Ruta para leer todos los tipos de subsidios
@router.get("/", response_model=List[schemas.TipoSubsidio])
def read_tipos_subsidios(db: Session = Depends(get_db)):
    return db.query(models.TipoSubsidio).all()

# Ruta para leer un tipo de subsidio por ID
@router.get("/{tipo_subsidio_id}", response_model=schemas.TipoSubsidio)
def read_tipo_subsidio(tipo_subsidio_id: int, db: Session = Depends(get_db)):
    tipo_subsidio = db.query(models.TipoSubsidio).filter(models.TipoSubsidio.id == tipo_subsidio_id).first()
    if tipo_subsidio is None:
        raise HTTPException(status_code=404, detail="Tipo de subsidio no encontrado")
    return tipo_subsidio

# Ruta para crear un nuevo tipo de subsidio
@router.post("/", response_model=schemas.TipoSubsidio)
def create_tipo_subsidio(tipo_subsidio: schemas.TipoSubsidioCreate, db: Session = Depends(get_db)):
    db_tipo_subsidio = models.TipoSubsidio(**tipo_subsidio.model_dump())
    db.add(db_tipo_subsidio)
    db.commit()
    db.refresh(db_tipo_subsidio)
    return db_tipo_subsidio

# Ruta para actualizar un tipo de subsidio existente
@router.put("/{tipo_subsidio_id}", response_model=schemas.TipoSubsidio)
def update_tipo_subsidio(tipo_subsidio_id: int, tipo_subsidio: schemas.TipoSubsidioCreate, db: Session = Depends(get_db)):
    db_tipo_subsidio = db.query(models.TipoSubsidio).filter(models.TipoSubsidio.id == tipo_subsidio_id).first()
    if db_tipo_subsidio is None:
        raise HTTPException(status_code=404, detail="Tipo de subsidio no encontrado")
    for key, value in tipo_subsidio.model_dump().items():
        setattr(db_tipo_subsidio, key, value)
    db.commit()
    db.refresh(db_tipo_subsidio)
    return db_tipo_subsidio

# Ruta para eliminar un tipo de subsidio
@router.delete("/{tipo_subsidio_id}")
def delete_tipo_subsidio(tipo_subsidio_id: int, db: Session = Depends(get_db)):
    db_tipo_subsidio = db.query(models.TipoSubsidio).filter(models.TipoSubsidio.id == tipo_subsidio_id).first()
    if db_tipo_subsidio is None:
        raise HTTPException(status_code=404, detail="Tipo de subsidio no encontrado")
    db.delete(db_tipo_subsidio)
    db.commit()
    return {"message": "Tipo de subsidio eliminado", "tipo_subsidio": db_tipo_subsidio}