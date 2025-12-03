from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from app.database import get_db
from app.controllers.favorito_controller import *
from fastapi.responses import RedirectResponse
from app.auth import verificar_token 
from app.models.usuario_model import UsuarioDB

router = APIRouter(prefix="/favoritos")
templates = Jinja2Templates(directory="app/views/templates")

@router.get("/")
def list_favorites(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("token")
    if not token:
        return RedirectResponse(url="/login", status_code=303)
        
    payload = verificar_token(token)
    if not payload:
        return RedirectResponse(url="/login", status_code=303)

    # pega id do usuário do token
    id_usuario = payload.get("id") or payload.get("id_usuario")

    # busca usuário no banco
    usuario = (
        db.query(UsuarioDB)
        .filter(UsuarioDB.id_cliente == id_usuario)
        .first()
    )

    if not usuario:
        return RedirectResponse(url="/login", status_code=303)

    # busca favoritos (produtos)
    favoritos = listar_favoritos(id_usuario, db)

    return templates.TemplateResponse(
        "favoritos.html",
        {
            "request": request,
            "favoritos": favoritos,  
            "usuario": usuario,
        },
    )


@router.post("/adicionar/{id_produto}")
def add_favorite(id_produto: int, request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("token")
    if not token:
        return RedirectResponse(url="/login", status_code=303)

    payload = verificar_token(token)
    if not payload:
        return RedirectResponse(url="/login", status_code=303)

    id_usuario = payload.get("id")

    return adicionar_favorito(id_usuario, id_produto, db)

@router.post("/deletar/{id_produto}")
def delete_favorite(id_produto: int, request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("token")
    if not token:
        return RedirectResponse(url="/login", status_code=303)

    payload = verificar_token(token)
    if not payload:
        return RedirectResponse(url="/login", status_code=303)

    id_usuario = payload.get("id")


    return remover_favorito(id_usuario, id_produto, db)
