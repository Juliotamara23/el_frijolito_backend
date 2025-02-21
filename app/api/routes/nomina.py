from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db import models, schemas
from app.db.database import get_db
from app.db.crud import crear_reporte_nomina, actualizar_reporte_nomina, eliminar_reporte_nomina
from uuid import UUID

router = APIRouter()

# Ruta para leer todas las nóminas
@router.get("/", response_model=List[schemas.ReporteNomina])
def leer_nominas(db: Session = Depends(get_db)):
    return db.query(models.ReporteNomina).all()

# Ruta para leer una nómina por su ID
@router.get("/{nomina_id}", response_model=schemas.ReporteNomina)
def leer_nomina(nomina_id: UUID, db: Session = Depends(get_db)):
    nomina = db.query(models.ReporteNomina).filter(models.ReporteNomina.id == nomina_id).first()
    if nomina is None:
        raise HTTPException(status_code=404, detail="Nómina no encontrada")
    return nomina

# Ruta para crear una nómina
@router.post("/", status_code=201, response_model=schemas.ReporteNomina)
def crear_nomina(nomina: schemas.ReporteNominaCreate, db: Session = Depends(get_db)):
    return crear_reporte_nomina(db, nomina)

# Ruta para actualizar una nómina
@router.put("/{nomina_id}", response_model=schemas.ReporteNomina)
def actualizar_nomina(nomina_id: UUID, nomina: schemas.ReporteNominaUpdate, db: Session = Depends(get_db)):
    return actualizar_reporte_nomina(db, nomina_id, nomina)

# Ruta para eliminar una nómina
@router.delete("/{nomina_id}")
def eliminar_nomina(nomina_id: UUID, db: Session = Depends(get_db)):
    return eliminar_reporte_nomina(db, nomina_id)