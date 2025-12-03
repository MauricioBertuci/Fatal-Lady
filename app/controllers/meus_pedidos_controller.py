from fastapi import Request
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from app.auth import verificar_token
from app.models.usuario_model import UsuarioDB
from app.models.pedido_model import PedidoDB, ItemPedidoDB
from app.controllers.produtos_controller import atribuir_imagem_para_produto

templates = Jinja2Templates(directory="app/views/templates")

def pedidos_usuario(request: Request, db: Session):
    token = request.cookies.get("token")
    payload = verificar_token(token)

    if not payload:
        return RedirectResponse(url="/login", status_code=303)

    email = payload.get("sub")
    usuario = db.query(UsuarioDB).filter_by(email=email).first()

    pedidos = (
        db.query(PedidoDB)
        .filter_by(id_cliente=usuario.id_cliente)
        .all()
    )

    # Garante imagem para cada produto dos itens de pedido
    for pedido in pedidos:
        for item in pedido.itens:
            if item.produto:
                atribuir_imagem_para_produto(item.produto)

    return templates.TemplateResponse(
        "meus_pedidos.html",
        {
            "request": request,
            "pedidos": pedidos,
            "usuario": usuario,
        },
    )
