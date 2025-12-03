from sqlalchemy.orm import joinedload
from app.controllers.produtos_controller import atribuir_imagem_para_produto
from fastapi.responses import RedirectResponse
from app.auth import verificar_token
from app.models import UsuarioDB, PedidoDB, ProdutoDB
from fastapi.templating import Jinja2Templates

templates =Jinja2Templates(directory="app/views/templates")
# Página inicial

def home_controller(request, db, templates):
    token = request.cookies.get("token")
    payload = verificar_token(token) if token else None

    usuario = None
    if payload:
        usuario = db.query(UsuarioDB).filter(UsuarioDB.email == payload["sub"]).first()

    # carrega produtos com categoria para o algoritmo de imagens funcionar
    produtos = (
        db.query(ProdutoDB)
        .options(joinedload(ProdutoDB.categoria))
        .order_by(ProdutoDB.id_produto)
        .all()
    )

    # aplica a mesma regra de imagem usada no catálogo/detalhe
    for produto in produtos:
        atribuir_imagem_para_produto(produto)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "usuario": usuario,
            "produtos": produtos,
        },
    )

# Painel do usuário
def painel_controller(request, db, templates):
    token = request.cookies.get("token")
    payload = verificar_token(token)
    if not payload:
        return RedirectResponse(url="/login", status_code=303)

    usuario = db.query(UsuarioDB).filter(UsuarioDB.email == payload["sub"]).first()
    if not usuario:
        return RedirectResponse(url="/login", status_code=303)

    pedidos = db.query(PedidoDB).filter(PedidoDB.id_cliente == usuario.id_cliente).all()

    return templates.TemplateResponse("painel_usuario.html", {
        "request": request,
        "usuario": usuario,
        "pedidos": pedidos
    })


# Meus dados
def meus_dados_controller(request, db, templates):
    token = request.cookies.get("token")
    payload = verificar_token(token)
    if not payload:
        return RedirectResponse(url="/login", status_code=303)

    usuario = db.query(UsuarioDB).filter(UsuarioDB.email == payload["sub"]).first()

    return templates.TemplateResponse("meus_dados.html", {
        "request": request,
        "usuario": usuario
    })

