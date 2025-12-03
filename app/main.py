from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# login google e facebook
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
import os

# Rotas
from app.routes.produto_router import router as produto_router
from app.routes.login_router import router as login_router
from app.routes.cadastro_router import router as cadastro_router
from app.routes.carrinho_router import router as carrinho_router
from app.routes.checkout_router import router as checkout_router
from app.routes.pagamento_router import router as pagamento_router
from app.routes.meus_pedidos_router import router as meus_pedidos_router
from app.routes.admin_router import router as admin_router
from app.routes.categoria_router import router as categoria_router
from app.routes.usuario_router import router as painel_usuario_router
from app.routes.logout_router import router as logout_router
from app.routes.favorito_router import router as favorito_router
from app.routes.redefinir_senha_router import router as redefinir_senha_router
from app.routes.frete_router import router as frete_router
from app.routes.excluir_conta_router import router as excluit_conta_router
from app.routes.endereco_router import router as endereco_router
from app.routes.politica_privacidade import router as termos_router
from app.routes.editar_usuario_router import router as editar_user_router
from app.routes.faq_router import router as faq_router
from app.routes.faleconosco_router import router as faleconosco_router
from app.routes.trocas_devolucoes_router import router as trocas_router

# Usuario Inativo
from datetime import datetime
from app.database import *
from app.models.usuario_model import UsuarioDB
import jwt
from app.auth import *
from jose import jwt, ExpiredSignatureError, JWTError

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




@app.middleware("http")
async def verificar_usuario_inativo(request, call_next):
    response = await call_next(request)

    token = request.cookies.get("token")
    if token:
        try:
            payload = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=[ALGORITHM]
            )

            user_id = payload.get("id")  # ID real do usuário

            if user_id:
                db = SessionLocal()
                user = db.query(UsuarioDB).filter(UsuarioDB.id_cliente == user_id).first()
                if user:
                    user.ultima_atividade = datetime.utcnow()
                    db.commit()
                db.close()

        # TOKEN EXPIRADO → ignora
        except ExpiredSignatureError:
            pass
        # TOKEN INVÁLIDO OU CORROMPIDO → ignora
        except JWTError:
            pass
        except Exception:
            pass

    return response



app.mount("/static", StaticFiles(directory="app/views/static"), name="static")

# --- Rotas públicas ---
app.include_router(login_router, tags=["Autenticação"])
app.include_router(logout_router, tags=["Autenticação"])
app.include_router(cadastro_router, tags=["Cadastro"])
app.include_router(redefinir_senha_router, tags=["Recuperação de Senha"])
app.include_router(produto_router, tags=["Produtos"])
app.include_router(categoria_router, tags=["Categorias"])
app.include_router(frete_router, tags=["Frete e Cep"])
app.include_router(termos_router, tags=["Termos"])
app.include_router(faq_router, tags=["Perguntas Frequente"])
app.include_router(trocas_router, tags=["Politicas"])
app.include_router(faleconosco_router, tags=["Fale Conosco"])

# --- Rotas de usuário autenticado ---
app.include_router(painel_usuario_router, tags=["Usuário"])
app.include_router(meus_pedidos_router, tags=["Pedidos"])
app.include_router(carrinho_router, tags=["Carrinho"])
app.include_router(checkout_router, tags=["Checkout"])
app.include_router(pagamento_router, tags=["Pagamentos"])
app.include_router(favorito_router, tags=["Favoritos"])
app.include_router(excluit_conta_router, tags=["Exclusão"])
app.include_router(endereco_router, tags=["Enderecos"])
app.include_router(editar_user_router, tags=["Editar Usuário"])
# app.include_router(usuario_inativo_router , tags=["Usuario Inativo"])

# --- Rotas administrativas ---
app.include_router(admin_router, tags=["Administração"])