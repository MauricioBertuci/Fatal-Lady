import requests
from fastapi import HTTPException, Request
from app.auth import verificar_token
from app.database import SessionLocal
from app.models.carrinho_model import *
from app.models.usuario_model import *

CEP_LOJA = "03008020"  # CEP SENAI

# def controller_calcular_frete(request: Request, cep_destino: str):
#     token = request.cookies.get("token")
#     payload = verificar_token(token)

#     if not payload:
#         raise HTTPException(status_code=401, detail="Usuário não autenticado")

#     # O token retorna e-mail, mas seu banco espera um INT.
#     user_id = payload.get("id")
#     if user_id is None:
#         raise HTTPException(status_code=401, detail="Token inválido: usuário sem ID")
    
#     try:
#         user_id_int = int(user_id)
#     except (TypeError, ValueError):
#         raise HTTPException(status_code=400, detail="Token inválido: ID do usuário não é um número")

#     cep_destino = cep_destino.strip().replace("-", "")
#     if not cep_destino.isdigit() or len(cep_destino) != 8:
#         raise HTTPException(status_code=400, detail="CEP inválido")

#     # Consulta ViaCep
#     via_cep_url = f"https://viacep.com.br/ws/{cep_destino}/json/"
#     resposta = requests.get(via_cep_url)
#     if resposta.status_code != 200:
#         raise HTTPException(status_code=400, detail="Erro ao consultar o CEP")

#     dados = resposta.json()
#     if "erro" in dados:
#         raise HTTPException(status_code=400, detail="CEP não encontrado")
#     db = SessionLocal()
#     try:
#         usuario = (
#             db.query(UsuarioDB)
#             .filter(UsuarioDB.id_cliente == user_id_int)
#             .first()
#         )

#         if not usuario:
#             raise HTTPException(status_code=400, detail="Usuário não encontrado")

#         carrinho = (
#             db.query(CarrinhoDB)
#             .filter(CarrinhoDB.id_cliente == usuario.id_cliente)
#             .first()
#         )
#     finally:
#         db.close()

#     # Sem carrinho = valor 0
#     total_compra = carrinho.valortotal if carrinho else 0

#     # Regras de frete
#     if total_compra >= 299:
#         valor_frete = 0.00
#         prazo_estimado = 4
#         status = "frete grátis aplicado"
#     else:
#         valor_frete = 15.00
#         prazo_estimado = 6
#         status = "simulação concluída"

#     return {
#         "endereco": f"{dados.get('logradouro')}, {dados.get('bairro')}, "
#                     f"{dados.get('localidade')}, {dados.get('uf')}",
#         "cep": cep_destino,
#         "valor_frete": valor_frete,
#         "prazo_estimado_dias": prazo_estimado,
#         "status": status
#     }

from sqlalchemy.orm import Session

def controller_calcular_frete(request: Request, cep_destino: str, db: Session):
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")

    payload = verificar_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")

    # AGORA USA O QUE REALMENTE EXISTE NO TOKEN: O E-MAIL
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Token inválido: e-mail ausente")

    # normaliza CEP
    cep_destino = cep_destino.strip().replace("-", "")
    if not cep_destino.isdigit() or len(cep_destino) != 8:
        raise HTTPException(status_code=400, detail="CEP inválido")

    # Consulta ViaCep
    via_cep_url = f"https://viacep.com.br/ws/{cep_destino}/json/"
    resposta = requests.get(via_cep_url, timeout=10)
    if resposta.status_code != 200:
        raise HTTPException(status_code=400, detail="Erro ao consultar o CEP")

    dados = resposta.json()
    if "erro" in dados:
        raise HTTPException(status_code=400, detail="CEP não encontrado")

    # usa o db injetado pelo FastAPI, nada de SessionLocal aqui
    usuario = (
        db.query(UsuarioDB)
        .filter(UsuarioDB.email == email)
        .first()
    )
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuário não encontrado")

    carrinho = (
        db.query(CarrinhoDB)
        .filter(CarrinhoDB.id_cliente == usuario.id_cliente)
        .first()
    )

    # Sem carrinho = valor 0
    total_compra = carrinho.valortotal if carrinho else 0

    # Regras de frete
    if total_compra >= 299:
        valor_frete = 0.00
        prazo_estimado = 4
        status = "frete grátis aplicado"
    else:
        valor_frete = 15.00
        prazo_estimado = 6
        status = "simulação concluída"

    return {
        "endereco": f"{dados.get('logradouro')}, {dados.get('bairro')}, "
                    f"{dados.get('localidade')}, {dados.get('uf')}",
        "cep": cep_destino,
        "valor_frete": valor_frete,
        "prazo_estimado_dias": prazo_estimado,
        "status": status,
    }

def controller_completar_cadastro(cep_destino: str):
    if not cep_destino.isdigit() or len(cep_destino) != 8:
        raise HTTPException(status_code=400, detail="CEP inválido")

    via_cep_url = f"https://viacep.com.br/ws/{cep_destino}/json/"
    resposta = requests.get(via_cep_url)

    if resposta.status_code != 200:
        raise HTTPException(status_code=400, detail="Erro ao consultar o CEP")

    dados = resposta.json()
    if "erro" in dados:
        raise HTTPException(status_code=400, detail="CEP não encontrado")

    return {
        "cep": cep_destino,
        "rua": dados.get("logradouro", ""),
        "bairro": dados.get("bairro", ""),
        "estado": dados.get("uf", ""),
        "cidade": dados.get("localidade", "")
    }
