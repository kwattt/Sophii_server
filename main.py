from quart_discord import DiscordOAuth2Session

from quart import Quart, send_from_directory
import asyncio
import os

from commons import loadFile
from config import configure_app

app = Quart(__name__, static_folder='build/build',static_url_path='')
configure_app(app)




#Inicializamos quart_discord.
discord_module = DiscordOAuth2Session(app)

# Registramos la API
from api.api_control import api_bp
app.register_blueprint(api_bp(discord_module))

@app.errorhandler(404)
async def react_router_handle(e):
  '''
    Este error handler enviará cualquier respuesta 404 a index.html, de esta manera el react-router se encargará 
    de renderizar los componentes necesarios. 
  ''' 
  return await send_from_directory(app.static_folder, 'index.html')

if __name__ == "__main__":
  if os.environ.get('DEVAREA') == 'True':
    app.run(debug=True)