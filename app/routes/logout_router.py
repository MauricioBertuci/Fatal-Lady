from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.controllers.logout_controler import *


router = APIRouter()

# Logout
@router.get("/logout")
def exit_account(request: Request):
    return logout_controller(request)
