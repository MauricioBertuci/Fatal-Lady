from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import Request
from fastapi.responses import RedirectResponse

from app.auth import verificar_token
from app.models.usuario_model import UsuarioDB
from app.models.carrinho_model import CarrinhoDB, ItemCarrinhoDB
from app.models.produto_model import ProdutoDB
from app.models.pedido_model import PedidoDB, ItemPedidoDB
from app.ultils import enviar_email
from app.ultils import tentar_registrar_lembrancinha
from app.models.lembrancinha_model import LembrancinhaDB
from sqlalchemy import func


def finalizar(request: Request, db: Session):
    token = request.cookies.get("token")
    if not token:
        return RedirectResponse(url="/login", status_code=303)
        
    payload = verificar_token(token)
    if not payload:
        return RedirectResponse(url="/login", status_code=303)

    email = payload.get("sub")
    usuario = db.query(UsuarioDB).filter_by(email=email).first()

    # Busca o carrinho atual
    carrinho = db.query(CarrinhoDB).filter_by(id_cliente=usuario.id_cliente).first()
    if not carrinho:
        return {"mensagem": "Carrinho vazio"}

    itens_carrinho = db.query(ItemCarrinhoDB).filter_by(carrinho_id=carrinho.id).all()
    if not itens_carrinho:
        return RedirectResponse(url="/carrinho?msg=empty", status_code=303)

    # Valida se todos os produtos ainda existem e possuem estoque suficiente
    produtos = {
        item.produto_id: db.query(ProdutoDB).filter_by(id_produto=item.produto_id).first()
        for item in itens_carrinho
    }

    for item in itens_carrinho:
        produto = produtos.get(item.produto_id)

        if not produto:
            return RedirectResponse(url="/carrinho?msg=product_missing", status_code=303)

        if produto.estoque < item.quantidade:
            return RedirectResponse(
                url=f"/carrinho?msg=out_of_stock&id={produto.id_produto}", status_code=303
            )

    # Calcula o total
    total = sum(item.quantidade * item.preco_unitario for item in itens_carrinho)

    # Cria o pedido
    pedido = PedidoDB(
        id_cliente=usuario.id_cliente,
        data=datetime.utcnow(),
        valortotal=total,
        status="Em processamento"
    )
    db.add(pedido)
    db.commit()
    db.refresh(pedido)

    # TENTA REGISTRAR LEMBRANCINHA AQUI
    ganhou_lembrancinha = tentar_registrar_lembrancinha(
        id_cliente=usuario.id_cliente,
        pedido_id=pedido.id,
        db=db,
    )

    # OPCIONAL: calcular quantas lembrancinhas ainda restam
    # (para mostrar no e-mail, se quiser)
    restantes = max(
        0,
        52 - (db.query(func.count(LembrancinhaDB.id)).scalar() or 0)
    )

    # Cria os itens do pedido
    for item in itens_carrinho:
        produto = produtos.get(item.produto_id)
        
        item_pedido = ItemPedidoDB(
            pedido_id=pedido.id,
            produto_id=item.produto_id,
            nome_produto=produto.nome if produto else "Produto removido",
            preco_unitario=produto.preco if produto else 0.0,
            quantidade=item.quantidade,
            tamanho=item.tamanho
        )
        db.add(item_pedido)

    db.commit()

    # Atualiza o estoque
    alterar_estoque(db, itens_carrinho)

    # salve os dados que serão usados, antes de apagar o carrinho
    itens_email = []
    for item in itens_carrinho:
        produto_nome = item.produto.nome
        itens_email.append({
            "nome": produto_nome,
            "quantidade": item.quantidade,
            "preco": item.preco_unitario
        })

    linhas_itens = ""
    for item in itens_email:
        subtotal = item["quantidade"] * item["preco"]
        linhas_itens += f"""
        <tr>
            <td>{item['nome']}</td>
            <td>{item['quantidade']}</td>
            <td>R$ {item['preco']:.2f}</td>
            <td>R$ {subtotal:.2f}</td>
        </tr>
        """

    # monta bloco opcional da lembrancinha para o e-mail
    bloco_lembrancinha = ""
    if ganhou_lembrancinha:
        bloco_lembrancinha = f"""
        <tr>
          <td colspan="4" style="padding:20px; background-color:#fff3cd; color:#856404; border-top:1px solid #ffeeba;">
            <strong>Parabéns!</strong> Você está entre as 50 pessoas selecionadas para retirar uma lembrancinha exclusiva.
            <br/>
            Apresente o código do seu pedido #{pedido.id} no ponto de retirada para receber.
          </td>
        </tr>
        """

    base_url = str(request.base_url).rstrip("/")
    url_meus_pedidos = f"{base_url}/me/meus-pedidos"

    html = f"""
    <html>
      <body style="font-family:'Poppins',Arial,sans-serif; background-color:#f9f9f9; padding:20px;">
        <table width="100%" cellpadding="0" cellspacing="0" style="max-width:600px; margin:auto; background:#fff; border-radius:10px; overflow:hidden;">
          <tr>
            <td align="center" style="padding:30px 0;">
              <h1 style="color:#000; font-size:26px;">FATAL <span style="color:#d00000;">LADY</span></h1>
              <p>Olá, <b>{usuario.nome}</b>! 👋</p>
              <p>Seu pedido foi <b>confirmado</b> e já está em processamento.</p>
            </td>
          </tr>

          <tr>
            <td style="padding:20px;">
              <h3>Resumo do Pedido:</h3>
              <table width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse; margin-top:10px;">
                <thead>
                  <tr style="background-color:#f2f2f2;">
                    <th style="padding:8px 12px; border:1px solid #ddd;">Produto</th>
                    <th style="padding:8px 12px; border:1px solid #ddd;">Qtd</th>
                    <th style="padding:8px 12px; border:1px solid #ddd;">Preço</th>
                    <th style="padding:8px 12px; border:1px solid #ddd;">Subtotal</th>
                  </tr>
                </thead>
                <tbody>
                  {linhas_itens}
                </tbody>
                <tfoot>
                  <tr style="background-color:#f2f2f2;">
                    <td colspan="3" style="padding:8px 12px; border:1px solid #ddd; text-align:right;"><b>Total:</b></td>
                    <td style="padding:8px 12px; border:1px solid #ddd; text-align:right;"><b>R$ {total:.2f}</b></td>
                  </tr>
                  {bloco_lembrancinha}
                </tfoot>
              </table>
            </td>
          </tr>

          <tr>
            <td align="center" style="padding:20px;">
              <a href="{url_meus_pedidos}" style="display:inline-block; background-color:#d00000; color:#fff; padding:14px 28px; border-radius:4px; text-decoration:none; font-weight:bold;">
                Acompanhar Pedido
              </a>
            </td>
          </tr>

          <tr>
            <td align="center" style="padding:20px; background-color:#000; color:#fff; font-size:13px;">
              <p>Frete grátis em compras acima de R$299</p>
              <p>© 2025 Fatal Lady. Todos os direitos reservados.</p>
            </td>
          </tr>
        </table>
      </body>
    </html>
    """

    enviar_email(
        destinatario=usuario.email,
        assunto="Pedido Confirmado",
        corpo=html
    )

    # Agora pode deletar os itens do carrinho
    for item in itens_carrinho:
        db.delete(item)
    db.commit()

    # Redireciona para a página de pagamentos
    return RedirectResponse(url=f"/pagamentos?pedido_id={pedido.id}", status_code=303)


def alterar_estoque(db: Session, itens_pedido):
    for item in itens_pedido:
        produto = db.query(ProdutoDB).filter_by(id_produto=item.produto_id).first()
        
        if produto:
            # Verifica se há estoque suficiente
            if produto.estoque >= item.quantidade:
                produto.estoque -= item.quantidade
            else:
                # Caso o estoque seja insuficiente, lança uma exceção
                raise ValueError(
                    f"Estoque insuficiente para o produto '{produto.nome}'. "
                    f"Disponível: {produto.estoque}, Solicitado: {item.quantidade}"
                )
        else:
            raise ValueError(f"Produto com ID {item.produto_id} não encontrado.")

    db.commit()
