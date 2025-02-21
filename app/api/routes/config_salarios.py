from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db import models, schemas
from app.db.database import get_db
from uuid import UUID

router = APIRouter()

# Ruta para leer las configuraciones de salarios
@router.get("/", response_model=List[schemas.ConfigSalario])
def leer_config_salarios(db: Session = Depends(get_db)):
    return db.query(models.ConfigSalario).all()