from sqlmodel import SQLModel, create_engine
from .config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

def init_db():
    SQLModel.metadata.create_all(engine)
