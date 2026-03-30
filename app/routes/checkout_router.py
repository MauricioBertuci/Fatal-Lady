from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.database import *
from app.auth import *
from app.controllers.checkout_controller import finalizar
from fastapi.templating import Jinja2Templates


router = APIRouter()

@router.post("/checkout")
def checkout(request:Request,db:Session=Depends(get_db)):
    return finalizar(request,db)

