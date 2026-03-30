import re
from app.models.usuario_model import UsuarioDB
from app.models.enderecos_model import EnderecoDB
from app.database import *
from app.auth import *
from fastapi import Request
from datetime import date
from sqlalchemy.orm import Session
from app.ultils import enviar_email, validar_cpf


def cadastro_controller(request: Request,
                        nome: str,
                        email: str,
                        senha: str,
                        cep: str,
                        rua: str,
                        cidade: str,
                        telefone: str,
                        complemento: str,
                        cpf: str,
                        genero: str,
                        data_nascimento: date,
                        bairro: str,
                        estado:str,
                        numero: str,
                        db: Session):
    # Verifica se o e-mail já existe
    usuario = db.query(UsuarioDB).filter(UsuarioDB.email == email).first()
    if usuario:
        return {"mensagem": "E-mail já cadastrado"}
    
    validator=validar_cpf(cpf)
    if validator == False:
        return  {"mensagem": "cpf invalido!"}


    # Cria o hash da senha e salva o usuário
    senha_hash = gerar_hash_senha(senha)
    novo_usuario = UsuarioDB(
        nome=nome,
        email=email,
        senha=senha_hash,
        telefone=telefone,
        cpf=cpf,
        genero=genero,
        data_nascimento=data_nascimento
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    # Cria o endereço vinculado
    novo_endereco = EnderecoDB(
        usuario_id=novo_usuario.id_cliente,
        cep=cep,
        rua=rua,
        bairro=bairro,
        cidade=cidade,
        estado=estado,
        complemento=complemento,
        numero=numero
    )

    db.add(novo_endereco)
    db.commit()

    # Envia e-mail de boas-vindas
    enviar_email(
        destinatario=email,
        assunto="Bem vindo a Fatal Lady", 
        corpo=
          f"""
  <html>
    <body style="margin:0; padding:0; font-family:'Poppins',Arial,sans-serif; background-color:#fff;">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td align="center" style="padding:40px 0;">
            <img src="views/static/upload/img/catalogo/icons-main/letreiro-logo.png" width="80" alt="Fatal Lady">
            <h1 style="color:#000; font-size:28px; margin-top:10px;">FATAL <span style="color:#d00000;">LADY</span></h1>
          </td>
        </tr>
        <tr>
          <td align="center" style="padding:20px 40px;">
            <h2>Olá, {nome}! 👋</h2>
            <p>Seja muito bem-vinda à <b>Fatal Lady</b> — onde a elegância encontra a atitude.</p>
            <p>Explore nossa coleção de saltos finos e sandálias exclusivas!</p>
            <a href="{request.base_url}login" style="display:inline-block; margin-top:20px; background-color:#d00000; color:#fff; padding:14px 28px; border-radius:4px; text-decoration:none; font-weight:bold;">
              Descubra Agora
            </a>
          </td>
        </tr>
        <tr>
          <td align="center" style="padding:40px 0; background-color:#000; color:#fff; font-size:13px;">
            <p>Frete grátis em compras acima de R$299</p>
            <p>© 2025 Fatal Lady. Todos os direitos reservados.</p>
          </td>
        </tr>
      </table>
    </body> 
  </html>""")

    return {"mensagem": "Usuário cadastrado com sucesso!"}


