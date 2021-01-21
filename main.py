from dotenv import load_dotenv, find_dotenv
import asyncio
import os
from quart import Quart, send_from_directory
from quart_session import Session
from quart_discord import DiscordOAuth2Session


from commons import loadFile
from config import configure_app

load_dotenv(find_dotenv())
app = Quart(__name__, static_folder='build/build',static_url_path='')
app.config['SESSION_TYPE'] = 'redis'
Session(app)
configure_app(app)

import psycopg2
from psycopg2 import Error

#Inicializamos quart_discord.
discord_module = DiscordOAuth2Session(app)

# Instancia de psycopg
dbase = None 

async def set_db():
    '''
    Cargamos la base de datos antes de servir cualquier petición
    '''

    try: 
        global dbase, dcursor
        dbase = psycopg2.connect(user="postgres",
                                password=os.environ.get('PSQL'),
                                host="127.0.0.1",
                                port="5432",
                                database="soph")

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
        exit()

asyncio.run(set_db())

# Registramos API
from api.api_control import api_bp
app.register_blueprint(api_bp(discord_module))

from api.api_social import social_bp
app.register_blueprint(social_bp(discord_module, dbase))

from api.api_msg import msg_bp
app.register_blueprint(msg_bp(discord_module, dbase))

from api.api_extra import extra_bp
app.register_blueprint(extra_bp(discord_module, dbase))

from api.api_requests import request_bp
app.register_blueprint(request_bp(discord_module, dbase))

from api.api_account import account_bp
app.register_blueprint(account_bp(discord_module, dbase))

from api.api_levels import levels_bp
app.register_blueprint(levels_bp(discord_module, dbase))

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