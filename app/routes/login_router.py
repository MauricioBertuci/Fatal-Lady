from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.requests import Request as StarletteRequest

from app.database import get_db
from app.controllers.login_controller import login_controller
from app.models.usuario_model import UsuarioDB
from app.auth import criar_token
from app.oauth_config import oauth
from app.ultils import enviar_email

router = APIRouter()
templates = Jinja2Templates(directory="app/views/templates")


# login

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login_post(
    request: Request,
    email: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db),
):
    return login_controller(request, email, senha, db)


#  LOGIN COM GOOGLE 
@router.get("/login/google")
async def login_google(request: Request):
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/login/google/callback", name="google_callback")
async def google_callback(
    request: Request,
    db: Session = Depends(get_db),
):
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception:
        # se vier direto sem ?code=..., volta pro login
        return RedirectResponse(url="/login", status_code=303)

    userinfo = token.get("userinfo")
    if not userinfo:
        userinfo = await oauth.google.parse_id_token(request, token)

    email = userinfo.get("email")
    nome = userinfo.get("name") or (email.split("@")[0] if email else "")

    if not email:
        return RedirectResponse(url="/login", status_code=303)

    # PROCURA USUÁRIO EXISTENTE
    usuario = db.query(UsuarioDB).filter(UsuarioDB.email == email).first()

    # SE NÃO EXISTE, CRIA UM NOVO A PARTIR DO GOOGLE
    if not usuario:
        usuario = UsuarioDB(
            nome=nome,
            email=email,
            # IMPORTANTE: aqui você PRECISA respeitar os campos obrigatórios do seu model.
            # Exemplos (AJUSTE para bater com seu UsuarioDB):

            # se 'senha' é NOT NULL:
            # - gere uma senha aleatória ou marque como "login_google"
            senha="login_google",  # ou um hash, se você sempre usa hash

            # se cpf / telefone / data_nascimento forem nullable=True, pode deixar None:
            # cpf=None,
            # telefone=None,
            # data_nascimento=None,

            # se tiver campos como:
            # is_admin=False,
            # ativo=True,
            # provedor="google",
        )

        db.add(usuario)
        db.commit()
        db.refresh(usuario)

            # Envia e-mail de boas-vindas
        logo_url = f"{request.base_url}/static/uploads/img/catalogo/icons-main/letreiro-logo.png"
        login_url = f"{request.base_url}/login"

        corpo_html = f"""
        <html>
            <body style="margin:0; padding:0; font-family:'Poppins',Arial,sans-serif; background-color:#fff;">
            <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                    <td align="center" style="padding:40px 0;">
                        <img src="{logo_url}" width="80" alt="Fatal Lady">
                        <h1 style="color:#000; font-size:28px; margin-top:10px;">
                            FATAL <span style="color:#d00000;">LADY</span>
                        </h1>
                    </td>
                </tr>
                <tr>
                    <td align="center" style="padding:20px 40px;">
                        <h2>Olá, {nome} 👋</h2>
                        <p>Seja muito bem-vinda à <b>Fatal Lady</b> — onde a elegância encontra a atitude.</p>
                        <p>Explore nossa coleção de saltos finos e sandálias exclusivas!</p>
                        <a href="{login_url}" style="display:inline-block; margin-top:20px; background-color:#d00000; color:#fff; padding:14px 28px; border-radius:4px; text-decoration:none; font-weight:bold;">
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
        </html>
        """

        enviar_email(
            destinatario=email,
            assunto="Bem-vinda à Fatal Lady",
            corpo=corpo_html,
        )   
    # A PARTIR DAQUI, JÁ TEMOS 'usuario' GARANTIDO

    # MESMA LÓGICA DO LOGIN NORMAL
    token_jwt = criar_token(
        {
            "sub": usuario.email,
            # ajuste as chaves conforme seu criar_token espera
            "id": usuario.id_cliente,
            "is_admin": usuario.is_admin,
        }
    )

    destino = "/admin" if getattr(usuario, "is_admin", False) else "/"
    response = RedirectResponse(url=destino, status_code=303)
    response.set_cookie(
        key="token",
        value=token_jwt,
        httponly=True,
        samesite="lax",
        secure=True,  # em produção/https -> True
        max_age=60 * 60 * 24 * 7,
    )
    return response