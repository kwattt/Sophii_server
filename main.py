from quart_discord import DiscordOAuth2Session

from quart import Quart, send_from_directory
import asyncio
import os
import aiosqlite

from commons import loadFile
from config import configure_app

app = Quart(__name__, static_folder='build/build',static_url_path='')
configure_app(app)

#Inicializamos quart_discord.
discord_module = DiscordOAuth2Session(app)

# Instancia de aiosqlite
dbase = None 
dcursor = None

async def set_db():
  '''
    Cargamos la base de datos antes de servir cualquier petición
  '''
  global dbase, dcursor
  dbase = await aiosqlite.connect('../config/test.db')
  dbase.row_factory = aiosqlite.Row
  dcursor = await dbase.cursor()
asyncio.run(set_db())

# Registramos API
from api.api_control import api_bp
app.register_blueprint(api_bp(discord_module))

from api.api_stream import stream_bp
app.register_blueprint(stream_bp(discord_module, dbase, dcursor))

from api.api_msg import msg_bp
app.register_blueprint(msg_bp(discord_module, dbase, dcursor))

from api.api_requests import request_bp
app.register_blueprint(request_bp(discord_module))



@app.errorhandler(404)
async def react_router_handle(e):
  '''
    Este error handler enviará cualquier respuesta 404 a index.html, de esta manera el react-router se encargará 
    de renderizar los componentes necesarios. 
  ''' 
  return await send_from_directory(app.static_folder, 'index.html')

if __name__ == "__main__":
  if os.environ.get('DEVAREA') == 'True':
    app.run(debug=True, port=5001)