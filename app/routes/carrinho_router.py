from fastapi import APIRouter, Form, Depends, Request
from fastapi.responses import HTMLResponse
from app.database import *
from sqlalchemy.orm import Session
from app.controllers.carrinho_controller import carrinho_add, carrinho_visualizar, carrinho_update, carrinho_remover
from fastapi.templating import Jinja2Templates
from app.database import get_db

router = APIRouter(prefix="/carrinho")

@router.get("/", response_class=HTMLResponse)
def list_items(request: Request, db: Session = Depends(get_db)):
    return carrinho_visualizar(request, db)

@router.post("/adicionar/{produto_id}")
def add(request:Request,
                        produto_id: int,
                        tamanho: int=Form(...),
                        quantidade: int=Form(1),
                        db:Session=Depends(get_db)
):
    return carrinho_add(request, produto_id, quantidade, tamanho, db)

@router.post("/editar/{produto_id}")
def update(
    request: Request,
    produto_id: int,
    tamanho: int = Form(...),
    quantidade: int = Form(...),
    db: Session = Depends(get_db)
):
    return carrinho_update(
    request=request,
    produto_id=produto_id,
    tamanho=tamanho,
    quantidade=quantidade,
    db=db
)


@router.post("/remover/{produto_id}")
def delete_item(
    request: Request,
    produto_id: int,
    db: Session = Depends(get_db)
):
    return carrinho_remover(request, produto_id, db)