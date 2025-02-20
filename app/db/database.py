from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from ..core.config import DATABASE_URL

# Crear el motor de conexión a la base de datos
engine = create_async_engine(DATABASE_URL)

# Crear una sesión para interactuar con la base de datos
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Base para definir modelos
Base = declarative_base()

# Definir la función get_async_db para obtener la sesión de la base de datos
async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session