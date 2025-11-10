from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
# login google e facebook
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
import os

from app.routes.produto_router import router as produto_router
from app.routes.login_router import router as login_router
from app.routes.cadastro_router import router as cadastro_router
from app.routes.carrinho_router import router as carrinho_router
from app.routes.checkout_router import router as checkout_router
from app.routes.meus_pedidos_router import router as meus_pedidos_router
from app.routes.admin_router import router as admin_router
from app.routes.categoria_router import router as categoria_router
from app.routes.usuario_router import router as painel_usuario_router
from app.routes.dashboard_router import router as dashboard_routes
from app.routes.logout_router import router as logout_router

from app.database import Base, engine
from app.models import *


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Loja de Sapatos")

# usado para login com google e facebook (antes das rotas)
load_dotenv()
app.add_middleware(
    SessionMiddleware,
    secret_key= os.getenv("SECRET_KEY", "FATALLADY@134"),  
    same_site="lax", 
    https_only=False,
    max_age=3600
)


app.mount("/static", StaticFiles(directory="app/views/static"), name="static")

app.include_router(produto_router)    
app.include_router(login_router)    
app.include_router(cadastro_router)
app.include_router(carrinho_router)   
app.include_router(checkout_router)   
app.include_router(meus_pedidos_router)   
app.include_router(admin_router)   
app.include_router(painel_usuario_router)   
app.include_router(categoria_router)
app.include_router(dashboard_routes)
app.include_router(logout_router)
 
