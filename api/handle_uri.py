import os
from commons import loadFile
import urllib.parse
import requests

# ¿Por qué hacerlo yo todo cuando alguien mas ya lo hizo y funciona bien?
from requests_oauthlib import OAuth2Session

def process_oauth(code):
  '''

    Procesar el código otorgado por discord para hacer el OAUTH2

    :param string code: 
      Código retornado por la autorización de discord.
    
    :returns:
      JSON con información de usuario.

  '''

  # TODO: 
  # No deberiamos de estar consultando las variables cada vez que esta función es llamada.

  development = os.environ.get('DEVAREA')
  config_pos = os.getenv('CONFIG_POS')
  cfg = loadFile(config_pos + "data.json")
  app_id = cfg["d_client_id"]
  app_secret = cfg["d_client_secret"]

  app_url = ""
  if development == 'True':
    app_url = cfg["d_oauth_local"]
  else:
    app_url = cfg["d_oauth"]

  headers = {
    "Content-Type": "application/x-www-form-urlencoded",
  }

  data = {
    "client_id": app_id,
    "client_secret": app_secret,
    "grant_type": "authorization_code",
    "code": code,
    "redirect_uri": app_url,
    "scope": "identity guilds"
  }

  response = requests.post("https://discord.com/api/oauth2/token", data=data, headers=headers)
  credentials = response.json()
  # Credenciales del usuario, deberiamos guardarlas.

  token = credentials["access_token"]
  response = requests.get("https://discord.com/api/v6/users/@me", headers={
    "Authorization": "Bearer {}".format(token)
  })
  
  print("called4")
  user = response.json()
  print(user)

  return user


def handle_uri():
  '''
    Return:
      Retorna el url que se utiliza para la autentificación de discord OAUTH2
  '''

  config_pos = os.getenv('CONFIG_POS')
  cfg = loadFile(config_pos + "data.json")

  development = os.environ.get('DEVAREA')
  app_id = cfg["d_client_id"]

  if development == 'True':
    app_url = cfg["d_oauth_local"]
  else:
    app_url = cfg["d_oauth"]

  app_scope = "identify%20guilds"
  return "https://discord.com/api/oauth2/authorize?client_id={}&redirect_uri={}&response_type=code&scope={}".format(app_id, urllib.parse.quote(app_url), app_scope)