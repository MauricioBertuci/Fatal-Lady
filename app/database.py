from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Dados do Supabase
USER = "postgres.xomisypdbkawfgzsddwn" 
PASSWORD = "FatalLady2026"
HOST = "aws-1-sa-east-1.pooler.supabase.com"
PORT = 6543
DBNAME = "postgres"
# URL de conexão com PostgreSQL (Supabase)
DATABASE_URL =  (
    f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"  
)
# Criar o engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True, 
)

# Criar sessões
SessionLocal = sessionmaker(bind=engine)

# Base para os models
Base = declarative_base()

# Dependência para injetar sessão (FastAPI)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




"""
from supabase import create_client, Client
from sqlalchemy.orm import declarative_base, sessionmaker

# --- Parte 1: Cliente Supabase (Auth, Storage, etc.) ---
SUPABASE_URL = "https://xomisypdbkawfgzsddwn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhvbWlzeXBkYmthd2ZnenNkZHduIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTc3NzMyMywiZXhwIjoyMDc1MzUzMzIzfQ.DqwT9AjxAc7L316ZkIEwOo9Ykuol71pPI68dBtK0Ox4"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Parte 2: Dummy SQLAlchemy para manter Base e get_db ---
# Base para declarar models (compatível com FastAPI)
Base = declarative_base()

# Criar sessões
SessionLocal = sessionmaker(bind=supabase)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"""