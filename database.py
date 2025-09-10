from sqlmodel import create_engine, Session, SQLModel
from contextlib import contextmanager
import os
import dotenv

dotenv.load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/biblioteca")

engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)


def create_tables():
    """Crear todas las tablas en la base de datos"""
    # Import models and metadata
    from models_transactional import (
        Book, Category, Stock, Scores, TaxRate,
        transactional_metadata
    )
    transactional_metadata.create_all(engine)


def drop_tables():
    """Eliminar todas las tablas de la base de datos"""
    # Import models and metadata
    from models_transactional import (
        Book, Category, Stock, Scores, TaxRate,
        transactional_metadata
    )
    transactional_metadata.drop_all(engine)


@contextmanager
def get_session():
    """Context manager para manejar sesiones de base de datos"""
    with Session(engine) as session:
        yield session