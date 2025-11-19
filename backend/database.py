from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql+psycopg2://neondb_owner:npg_rA6bLJpsz8yY@ep-fragrant-cloud-adf9oczc-pooler.c-2.us-east-1.aws.neon.tech/ecommerce?sslmode=require"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,     # <-- verifica conexiones vivas
    pool_recycle=300,       # <-- recicla conexiones viejas
    pool_size=5,            # <-- 5 conexiones vivas
    max_overflow=10         # <-- permite 10 más temporales
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
