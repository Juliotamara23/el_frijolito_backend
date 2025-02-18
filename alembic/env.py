from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
import os

# Agregar el directorio del proyecto al PATH para importar config.py correctamente
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar la configuración de la base de datos desde config.py
from app.core.config import DATABASE_URL
from app.db.database import Base  # Importa la base para reflejar modelos

# Cargar la configuración de logging desde alembic.ini
config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

# Configurar la URL de la base de datos dinámicamente
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Definir los modelos a considerar en la migración
target_metadata = Base.metadata

# Función para ejecutar migraciones en modo offline
def run_migrations_offline():
    """Ejecuta las migraciones en 'modo offline' sin conectar un motor SQLAlchemy."""
    context.configure(url=DATABASE_URL, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

# Función para ejecutar migraciones en modo online
def run_migrations_online():
    """Ejecuta las migraciones en 'modo online' creando un engine de SQLAlchemy."""
    connectable = engine_from_config(config.get_section(config.config_ini_section), prefix="sqlalchemy.", poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

# Determinar si ejecutamos en modo online u offline
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()