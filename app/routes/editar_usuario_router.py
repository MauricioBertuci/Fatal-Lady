from fastapi import APIRouter, Depends, Request, Form
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app.controllers.editar_usuario_controller import editar_usuario_controller
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/me")

@router.post("/editar/dados")
def editar_usuario(
    request: Request,
    nome: str = Form(...),
    email: str = Form(...),
    telefone: str = Form(...),
    genero: str = Form(...),
    cpf: str = Form(...),
    data_nascimento: date = Form(...),
    db: Session = Depends(get_db)
):
    return editar_usuario_controller(
        request, db, nome, email, telefone, genero, cpf, data_nascimento
    )