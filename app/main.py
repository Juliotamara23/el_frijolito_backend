from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .api.routes.api import api_router
from app.db.database import get_db

app = FastAPI(title="API de Nómina Tu Casa Ya")
app.include_router(api_router)

@app.get("/")
def read_root(db: Session = Depends(get_db)):
    return {"message": "Bienvenido a la API de Nómina Tu Casa Ya"}