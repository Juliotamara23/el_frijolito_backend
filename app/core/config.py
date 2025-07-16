from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData
from dotenv import dotenv_values

# Configuración de la base de datos
metadata = MetaData()
Base = declarative_base()

# Obtener variables de entorno del archivo .env
config = dotenv_values("./.env")
username = config.get("DATABASE_USERNAME")
password = config.get("DATABASE_PASSWORD")
dbname = config.get("DATABASE_NAME")
port = config.get("DATABASE_PORT")
host = config.get("DATABASE_HOST")

# URL de conexión usando el driver asíncrono de postgresql
DATABASE_URL = f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{dbname}"

async def db_connect():
    # Crear conexión a la base de datos
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        return engine, conn

async def create_tables(engine):
    # Crear tablas usando metadata
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)

async def create_tables_orm(engine):
    # Crear tablas usando ORM
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

def get_session():
    # Configurar sesión asíncrona
    engine = create_async_engine(DATABASE_URL)
    AsyncSessionLocal = AsyncSession(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    return AsyncSessionLocal

# Para usar en main.py
AsyncSessionLocal = get_session()