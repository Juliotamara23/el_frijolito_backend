from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db import models, schemas
from app.db.database import get_db

router = APIRouter()

# Ruta para leer todos los tipos de descuentos
@router.get("/", response_model=List[schemas.TipoDescuento])
def leer_tipos_descuentos(db: Session = Depends(get_db)):
    return db.query(models.TipoDescuento).all()

# Ruta para leer un tipo de descuento por su ID
@router.get("/{tipo_descuento_id}", response_model=schemas.TipoDescuento)
def leer_tipo_descuento(tipo_descuento_id: int, db: Session = Depends(get_db)):
    tipo_descuento = db.query(models.TipoDescuento).filter(models.TipoDescuento.id == tipo_descuento_id).first()
    if tipo_descuento is None:
        raise HTTPException(status_code=404, detail="Tipo de descuento no encontrado")
    return tipo_descuento

# Ruta para crear un tipo de descuento
@router.post("/", status_code=201, response_model=schemas.TipoDescuento)
def crear_tipo_descuento(tipo_descuento: schemas.TipoDescuentoCreate, db: Session = Depends(get_db)):
    nuevo_tipo_descuento = models.TipoDescuento(**tipo_descuento.model_dump())
    db.add(nuevo_tipo_descuento)
    db.commit()
    db.refresh(nuevo_tipo_descuento)
    return nuevo_tipo_descuento

# Ruta para actualizar un tipo de descuento
@router.put("/{tipo_descuento_id}", response_model=schemas.TipoDescuento)
def actualizar_tipo_descuento(tipo_descuento_id: int, tipo_descuento: schemas.TipoDescuentoUpdate, db: Session = Depends(get_db)):
    db_tipo_descuento = db.query(models.TipoDescuento).filter(models.TipoDescuento.id == tipo_descuento_id).first()
    if db_tipo_descuento is None:
        raise HTTPException(status_code=404, detail="Tipo de descuento no encontrado")
    for key, value in tipo_descuento.model_dump(exclude_unset=True).items():
        setattr(db_tipo_descuento, key, value)
    db.commit()
    db.refresh(db_tipo_descuento)
    return db_tipo_descuento

# Ruta para eliminar un tipo de descuento
@router.delete("/{tipo_descuento_id}")
def eliminar_tipo_descuento(tipo_descuento_id: int, db: Session = Depends(get_db)):
    db_tipo_descuento = db.query(models.TipoDescuento).filter(models.TipoDescuento.id == tipo_descuento_id).first()
    if db_tipo_descuento is None:
        raise HTTPException(status_code=404, detail="Tipo de descuento no encontrado")
    db.delete(db_tipo_descuento)
    db.commit()
    return {"message": "Tipo de descuento eliminado exitosamente", "tipo_descuento": db_tipo_descuento}