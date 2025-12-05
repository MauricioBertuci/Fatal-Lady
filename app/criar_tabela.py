from database import Base, engine
from models import LembrancinhaDB
from models import UsuarioDB
print("🔧 Criando tabelas no banco de dados...")
Base.metadata.create_all(bind=engine)
print("✅ Tabelas criadas com sucesso!")
