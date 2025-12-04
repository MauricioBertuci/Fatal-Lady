import smtplib
import re
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText

load_dotenv()
EMAIL_REMITENTE = os.getenv("EMAIL_REMITENTE")
EMAIL_SENHA = os.getenv("EMAIL_SENHA")
EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", EMAIL_REMITENTE)


from fastapi import Request
from app.auth import verificar_token
def _get_usuario_id(request: Request):
    token = request.cookies.get("token")
    if not token:
        return None
    payload = verificar_token(token)
    if not payload:
        return None
    return payload.get("id")


def validar_cpf(cpf: str) -> bool: #bool: faz retornar True ou False
    #remove tudo que não for número
    #\D: qualquer coisa que não seja numero
    #\d: qualquer numero de 0 a 9
    #função re substitui "x" por "y"
    cpf = str(cpf)
    cpf = re.sub(r"\D", "", cpf)

    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    
    #fazendo calculo par ver se é valido o cpf
    for i in range(9, 11):
        soma = sum(int(cpf[j]) * ((i + 1) - j) for j in range(i))
        digito = (soma * 10 % 11) % 10
        if digito != int(cpf[i]):
            return False
    return True

def enviar_email(destinatario, assunto, corpo):
    msg = MIMEText(corpo, "html", "utf-8")
    msg["Subject"] = assunto
    msg["From"] = EMAIL_FROM_NAME  # remetente correto
    msg["To"] = destinatario

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_REMITENTE, EMAIL_SENHA)  # login correto
        server.send_message(msg)



from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models.usuario_model import UsuarioDB


def verificar_inativos():
    db = SessionLocal()
    limite = datetime.utcnow() - timedelta(days=30)

    inativos = db.query(UsuarioDB).filter(UsuarioDB.ultima_atividade < limite).all()

    for user in inativos:
        enviar_email(
            user.email,
            assunto="Sentimos sua falta 💛",
            corpo=f"""<html>
  <body style="margin:0; padding:0; font-family:'Poppins',Arial,sans-serif; background-color:#fff;">
    <table width="100%" cellpadding="0" cellspacing="0">
      <tr>
        <td align="center" style="padding:40px 0;">
          <img src="views/static/upload/img/catalogo/icons-main/letreiro-logo.png" width="80" alt="Fatal Lady">
          <h1 style="color:#000; font-size:28px; margin-top:10px;">
            FATAL <span style="color:#d00000;">LADY</span>
          </h1>
        </td>
      </tr>
      <tr>
        <td align="center" style="padding:20px 40px; max-width:600px; margin:0 auto;">
          <h2 style="color:#000;">Olá, {user.nome}! 👋</h2>

          <p style="font-size:15px; color:#333; line-height:1.6; margin-top:10px;">
            Percebemos que faz <b>1 mês</b> desde seu último acesso à nossa plataforma.
          </p>

          <p style="font-size:15px; color:#333; line-height:1.6;">
            A Fatal Lady está cheia de <b>novidades incríveis</b> que você vai amar — incluindo novos lançamentos, promoções exclusivas e coleções que acabaram de chegar!
          </p>

          <a href="https://fatallady.chilecentral.cloudapp.azure.com/"
            style="display:inline-block;
                   margin-top:25px;
                   background-color:#d00000;
                   color:#fff;
                   padding:14px 28px;
                   border-radius:4px;
                   text-decoration:none;
                   font-weight:bold;">
            Voltar para a loja
          </a>
        </td>
      </tr>
      <tr>
        <td align="center" style="padding:40px 0; background-color:#000; color:#fff; font-size:13px;">
          <p style="margin:5px 0;">Frete grátis em compras acima de R$299</p>
          <p style="margin:5px 0;">© 2025 Fatal Lady. Todos os direitos reservados.</p>
        </td>
      </tr>

    </table>
  </body>
</html>
"""
)
    db.close()


scheduler = BackgroundScheduler()
# scheduler.add_job(verificar_inativos, "interval", seconds=10) 
scheduler.add_job(verificar_inativos, "cron", hour=0) # executa todo dia às 00:00
scheduler.start()
