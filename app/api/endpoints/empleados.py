from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db import models, schemas
from app.db.database import get_db  # Importar get_db correctamente

router = APIRouter()

@router.get("/", response_model=List[schemas.Empleado])
def leer_empleados(db: Session = Depends(get_db)):  # Usar get_db aquí
    return db.query(models.Empleado).all()