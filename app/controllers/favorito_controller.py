from fastapi import HTTPException
from sqlalchemy.orm import Session
from fastapi import Request
from app.models.favorito_model import FavoritoDB
from app.models.produto_model import ProdutoDB
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from app.controllers.produtos_controller import atribuir_imagem_para_produto

templates = Jinja2Templates(directory="app/views/templates")

def listar_favoritos(id_usuario: int, db: Session):
    favoritos = (
        db.query(FavoritoDB)
        .filter(FavoritoDB.id_usuario == id_usuario)
        .all()
    )

    # pega a lista de ProdutoDB
    produtos = [f.produto for f in favoritos]

    # aplica a mesma regra de imagem do catálogo/produto
    for produto in produtos:
        atribuir_imagem_para_produto(produto)

    return produtos


def adicionar_favorito(id_usuario: int, id_produto: int, db: Session):
    produto = db.query(ProdutoDB).filter(ProdutoDB.id_produto == id_produto).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    favorito_existente = db.query(FavoritoDB).filter_by(id_usuario=id_usuario, id_produto=id_produto).first()
    if favorito_existente:
        raise HTTPException(status_code=400, detail="Produto já está nos favoritos")

    favorito = FavoritoDB(id_usuario=id_usuario, id_produto=id_produto)
    db.add(favorito)
    db.commit()
    db.refresh(favorito)
    return RedirectResponse(url="/favoritos", status_code=303)

def remover_favorito(id_usuario: int, id_produto: int, db: Session):
    favorito = db.query(FavoritoDB).filter_by(id_usuario=id_usuario, id_produto=id_produto).first()
    if not favorito:
        raise HTTPException(status_code=404, detail="Favorito não encontrado")

    db.delete(favorito)
    db.commit()
    return RedirectResponse(url="/favoritos", status_code=303)
