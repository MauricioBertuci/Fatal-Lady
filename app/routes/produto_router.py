from fastapi import APIRouter, Request, Form, File, Depends 
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import unicodedata
from collections import defaultdict
from sqlalchemy.orm import Session
from app.database import get_db
from app.controllers.produtos_controller import *

router = APIRouter() #rotas

#pasta para dalvar imagens
UPLOAD_DIR= "views/static/uploads"
#caminhos para o os
os.makedirs(UPLOAD_DIR,exist_ok=True)

#rota para pagina listar produtos
@router.get("/produtos", response_class=HTMLResponse)
async def get_listar_produtos(request: Request, db: Session = Depends(get_db)):
    return produtos_por_categoria(request, db)

@router.get("/categoria", response_class=HTMLResponse)
async def get_produtos_categoria(request: Request, db: Session = Depends(get_db)):
    return produtos_por_categoria(request, db)

#rota para detalhar produto
@router.get("/produto-get/{id_produto}", response_class=HTMLResponse)
async def get_detalhe_produto(request: Request, id_produto: int, db: Session = Depends(get_db)):
    return get_produto(request, id_produto, db)



