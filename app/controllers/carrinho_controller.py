from fastapi import Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime

from app.auth import verificar_token
from app.models.usuario_model import UsuarioDB
from app.models.carrinho_model import CarrinhoDB, ItemCarrinhoDB
from app.models.produto_model import ProdutoDB
from fastapi.templating import Jinja2Templates
from app.controllers.produtos_controller import atribuir_imagem_para_produto


templates = Jinja2Templates(directory="app/views/templates")

#  ADICIONAR ITEM AO CARRINHO 
def carrinho_add(request: Request, id_produto: int, quantidade: int, tamanho: int, db: Session):
    token = request.cookies.get("token")
    payload = verificar_token(token)

    if not payload:
        return RedirectResponse(url="/login", status_code=303)

    email = payload.get("sub")
    usuario = db.query(UsuarioDB).filter_by(email=email).first()

    if not usuario:
        return RedirectResponse(url="/login", status_code=303)
    produto = db.query(ProdutoDB).filter_by(id_produto=id_produto).first()

    if not produto:
        return {"mensagem": "Produto não encontrado"}

    # Verifica se o carrinho do usuário já existe
    carrinho = db.query(CarrinhoDB).filter_by(id_cliente=usuario.id_cliente).first()

    if not carrinho:
        carrinho = CarrinhoDB(
            id_cliente=usuario.id_cliente,
            data=datetime.utcnow(),
            valortotal=0.0
        )
        db.add(carrinho)
        db.commit()
        db.refresh(carrinho)

    # Verifica se o produto (com o mesmo tamanho) já está no carrinho
    item = (
        db.query(ItemCarrinhoDB)
        .filter_by(carrinho_id=carrinho.id, produto_id=id_produto, tamanho=tamanho)
        .first()
    )

    if item:
        item.quantidade += quantidade
    else:
        item = ItemCarrinhoDB(
            carrinho_id=carrinho.id,
            produto_id=id_produto,
            quantidade=quantidade,
            preco_unitario=produto.preco,
            tamanho=tamanho
        )
        db.add(item)

    # Atualiza o valor total do carrinho
    db.commit()
    itens = db.query(ItemCarrinhoDB).filter_by(carrinho_id=carrinho.id).all()
    carrinho.valortotal = sum(item.quantidade * item.preco_unitario for item in itens)
    db.commit()

    return RedirectResponse(url="/carrinho", status_code=303)


#  REMOVER ITEM 
def carrinho_remover(request: Request, produto_id: int, db: Session):
    token = request.cookies.get("token")
    payload = verificar_token(token)

    if not payload:
        return RedirectResponse(url="/login", status_code=303)

    email = payload.get("sub")
    usuario = db.query(UsuarioDB).filter_by(email=email).first()
    if not usuario:
        return RedirectResponse(url="/login", status_code=303)

    carrinho = db.query(CarrinhoDB).filter_by(id_cliente=usuario.id_cliente).first()

    if not carrinho:
        return RedirectResponse(url="/carrinho", status_code=303)

    item = (
        db.query(ItemCarrinhoDB)
        .filter_by(carrinho_id=carrinho.id, produto_id=produto_id)
        .first()
    )

    if item:
        db.delete(item)
        db.commit()

        # Recalcula o total
        itens = db.query(ItemCarrinhoDB).filter_by(carrinho_id=carrinho.id).all()
        carrinho.valortotal = sum(item.quantidade * item.preco_unitario for item in itens)
        db.commit()

    return RedirectResponse(url="/carrinho", status_code=303)


#  ATUALIZAR QUANTIDADE 
def carrinho_update(request: Request, produto_id: int, tamanho: int, quantidade: int, db: Session):
    token = request.cookies.get("token")
    payload = verificar_token(token)

    if not payload:
        return RedirectResponse(url="/login", status_code=303)

    email = payload.get("sub")
    usuario = db.query(UsuarioDB).filter_by(email=email).first()
    if not usuario:
        return RedirectResponse(url="/login", status_code=303)
    carrinho = db.query(CarrinhoDB).filter_by(id_cliente=usuario.id_cliente).first()

    if not carrinho:
        return RedirectResponse(url="/carrinho", status_code=303)

    item = (
        db.query(ItemCarrinhoDB)
        .filter_by(carrinho_id=carrinho.id, produto_id=produto_id, tamanho=tamanho)
        .first()
    )

    if item:
        item.quantidade = quantidade
        db.commit()

        # Recalcula o total
        itens = db.query(ItemCarrinhoDB).filter_by(carrinho_id=carrinho.id).all()
        carrinho.valortotal = sum(item.quantidade * item.preco_unitario for item in itens)
        db.commit()

    return RedirectResponse(url="/carrinho", status_code=303)


#  VISUALIZAR CARRINHO 
def carrinho_visualizar(request: Request, db: Session):
    token = request.cookies.get("token")

    if not token:
        return RedirectResponse(url="/login", status_code=303) 
    
    payload = verificar_token(token)

    if not payload:
        return RedirectResponse(url="/login", status_code=303)

    email = payload.get("sub")
    usuario = db.query(UsuarioDB).filter_by(email=email).first()
    if not usuario:
        return RedirectResponse(url="/login", status_code=303)

    carrinho = db.query(CarrinhoDB).filter_by(id_cliente=usuario.id_cliente).first()

    if not carrinho:
        return templates.TemplateResponse(
            "carrinho.html",
            {"request": request, "carrinho": [], "total": 0.0, "usuario": usuario}
        )

    itens = (
        db.query(ItemCarrinhoDB)
        .filter_by(carrinho_id=carrinho.id)
        .all()
    )

    # aplica imagem para cada produto do item
    for item in itens:
        if item.produto:
            atribuir_imagem_para_produto(item.produto)

    total = sum(item.quantidade * item.preco_unitario for item in itens)

    return templates.TemplateResponse(
        "carrinho.html",
        {
            "request": request,
            "carrinho": itens,
            "total": total,
            "usuario": usuario,
        }
    )
