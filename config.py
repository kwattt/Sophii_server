import os 
from commons import loadFile

def configure_app(app):

  ''' 
    Añade los atributos necesarios a nuestra aplicación y al entorno de trabajo.

    Parametros:
      app:
        Objeto de aplicación de Quart
  '''

  config_pos = os.getenv('CONFIG_POS')

  cfg = loadFile(config_pos + "data.json")

  app.secret_key = cfg["app_secret"]
  app.config["DISCORD_CLIENT_ID"] = cfg["d_client_id"]
  app.config["DISCORD_CLIENT_SECRET"] = cfg["d_client_secret"]
  app.config["DISCORD_BOT_TOKEN"] = cfg["d_bot_token"]

  development = os.environ.get('DEVAREA')
  if development == 'True':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.config["DISCORD_REDIRECT_URI"] = cfg["d_oauth_local"]
    print("DEV -- DETECTED")
  else:
    app.config["DISCORD_REDIRECT_URI"] = cfg["d_oauth"]
