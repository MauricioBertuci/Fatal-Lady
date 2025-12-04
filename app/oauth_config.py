from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from dotenv import load_dotenv
import os

BASE_DIR = os.path.dirname(__file__)
ENV_PATH = os.path.join(BASE_DIR, ".env")

# Carrega variáveis do .env
load_dotenv(ENV_PATH)

config = Config(ENV_PATH)
oauth = OAuth(config)

# Login com Google (OAuth2 / OpenID Connect)
oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID") or config("GOOGLE_CLIENT_ID", default=None),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET") or config("GOOGLE_CLIENT_SECRET", default=None),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

# Login com Facebook (mantive sua config)
oauth.register(
    name="facebook",
    client_id=os.getenv("FACEBOOK_CLIENT_ID"),
    client_secret=os.getenv("FACEBOOK_CLIENT_SECRET"),
    access_token_url='https://graph.facebook.com/v21.0/oauth/access_token',
    authorize_url='https://www.facebook.com/v21.0/dialog/oauth',
    api_base_url='https://graph.facebook.com/v21.0/',
    client_kwargs={'scope': 'email public_profile'}
)
