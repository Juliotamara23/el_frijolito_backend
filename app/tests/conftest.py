import pytest
import asyncio
import platform
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base, Empleado, ConfigSalario, TipoRecargo, TipoDescuento, TipoSubsidio
from dotenv import dotenv_values

# Obtener variables de entorno del archivo .env
config = dotenv_values("./.env")
username = config.get("DATABASE_USERNAME_TEST")
password = config.get("DATABASE_PASSWORD_TEST")
dbname = config.get("DATABASE_NAME_TEST")
port = config.get("DATABASE_PORT_TEST")
host = config.get("DATABASE_HOST_TEST")

# URL de conexión usando el driver asíncrono de postgresql
TEST_DATABASE_URL = f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{dbname}"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def engine():
    """Create a SQLAlchemy engine instance for test database."""
    _engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=True,
        future=True,
        pool_size=1,
        max_overflow=0
    )
    
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield _engine
    
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await _engine.dispose()

@pytest.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a new database session for a test."""
    Session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )

    async with Session() as session:
        yield session
        await session.rollback()