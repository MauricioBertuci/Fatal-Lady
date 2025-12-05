from fastapi import APIRouter, Request, Query, Depends
from app.controllers.frete_controller import *

router = APIRouter(prefix="/frete")

# @router.get("/calcular/")
# def calcular_frete(request: Request, 
#                    cep_destino: str = Query(...)):
#     return controller_calcular_frete(request, cep_destino)
from sqlalchemy.orm import Session
@router.get("/calcular")
def calcular_frete(
    request: Request,
    cep_destino: str,
    db: Session = Depends(get_db),
):
    return controller_calcular_frete(request, cep_destino, db)


@router.get("/completar_cadastro/{cep_destino}")
def completar_cadastro(cep_destino: str):
    return controller_completar_cadastro(cep_destino)
