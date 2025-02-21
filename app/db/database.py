from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from ..core.config import DATABASE_URL

# Crea el motor de base de datos
engine = create_async_engine(DATABASE_URL)

# Crea una sesión asíncrona
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Crea la base de datos declarativa
Base = declarative_base()

# Definición de la función get_db
async def get_db():
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()