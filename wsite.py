from commons import loadFile
from quart_discord import DiscordOAuth2Session
from discord.ext.ipc import Client
from discord.ext import commands
from quart import Quart, blueprints, redirect
import asyncio

app = Quart(__name__)
cfg = loadFile("config/data.json")
web_ipc = Client(secret_key=cfg["IPC_key"])

# CONFIG
app.secret_key = cfg["flask_secret"]
app.config["DISCORD_CLIENT_ID"] = cfg["d_client_id"]
app.config["DISCORD_CLIENT_SECRET"] = cfg["d_client_secret"]
app.config["DISCORD_REDIRECT_URI"] = cfg["d_oauth"]
app.config["DISCORD_BOT_TOKEN"] = cfg["d_bot_token"]

# TESTING
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

discords = DiscordOAuth2Session(app)

# no index atm.

from bp.panel import panel    
app.register_blueprint(panel)

@app.route("/")
async def tarde():
    return redirect("/panel/")