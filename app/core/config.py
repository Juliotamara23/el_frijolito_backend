from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import dotenv_values

metadata = MetaData()
Base = declarative_base()

config = dotenv_values("./.env")  # Lee las variables de entorno desde .env
username = config.get("DATABASE_USERNAME")
password = config.get("DATABASE_PASSWORD")
dbname = config.get("DATABASE_NAME")
port = config.get("DATABASE_PORT")
host = config.get("DATABASE_HOST")

# Construye la URL de conexión usando f-strings
DATABASE_URL = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{dbname}" 

def db_connect():
    engine = create_engine(DATABASE_URL, echo=True)  # echo=True para ver logs de SQL
    connection = engine.connect()

    return engine, connection

def create_tables(engine):
    metadata.drop_all(engine, checkfirst=True) # Elimina las tablas existentes y las vuelve a crear.
    metadata.create_all(engine, checkfirst=True) # Crea las tablas si no existen.

def create_tables_orm(engine):
    Base.metadata.drop_all(engine, checkfirst=True)
    Base.metadata.create_all(engine, checkfirst=True)

def create_session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()

    return session

# Para usar en main.py:
engine, connection = db_connect() # Obtener el motor y la conexión.
SessionLocal = sessionmaker(bind=engine) # Crear la sesión local.