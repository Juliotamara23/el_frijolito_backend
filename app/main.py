from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .api.routes.api import api_router
from app.db.database import get_db

app = FastAPI(title="API de Nómina")

# Configurar CORS
origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],         # Permite todos los métodos HTTP
    allow_headers=["*"],         # Permite todas las cabeceras
)

app.include_router(api_router)

@app.get("/")
def read_root(db: Session = Depends(get_db)):
    return {"message": "Bienvenido a la API del restaurante el frijolito"}