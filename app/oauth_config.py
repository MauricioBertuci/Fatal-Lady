
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from dotenv import load_dotenv
import os

BASE_DIR = os.path.dirname(__file__)
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

config = Config(os.path.join(os.path.dirname(__file__), ".env"))
oauth = OAuth(config)

#  Login com Google (OAuth2 / OpenID Connect)
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=os.getenv("GOOGLE_CLIENT_ID") or config("GOOGLE_CLIENT_ID", default=None),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET") or config("GOOGLE_CLIENT_SECRET", default=None),
    client_kwargs={"scope": "openid email profile"},
)

facebook = oauth.register(
    name='facebook',
    client_id=os.getenv("FACEBOOK_CLIENT_ID"),
    client_secret=os.getenv("FACEBOOK_CLIENT_SECRET"),
    access_token_url='https://graph.facebook.com/v21.0/oauth/access_token',  # ← v21
    authorize_url='https://www.facebook.com/v21.0/dialog/oauth',  # ← v21
    api_base_url='https://graph.facebook.com/v21.0/',  # ← v21
    client_kwargs={'scope': 'email public_profile'}
)