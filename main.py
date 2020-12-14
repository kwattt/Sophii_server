from commons import loadFile
from quart_discord import DiscordOAuth2Session
from discord.ext.ipc import Client
from discord.ext import commands
from quart import Quart, blueprints, redirect, send_from_directory
import asyncio
import os

config_pos = os.getenv('CONFIG_POS')

cfg = loadFile(config_pos + "data.json")
web_ipc = Client(secret_key=cfg["IPC_key"])

app = Quart(__name__, static_folder='build/build',static_url_path='')
app.secret_key = cfg["flask_secret"]
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

@app.route('/')
async def serve():
  return await send_from_directory(app.static_folder, 'index.html')

if development == 'True':
  if __name__ == "__main__":
    app.run(debug=True)
