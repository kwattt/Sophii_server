from quart import Blueprint, redirect, jsonify, request, url_for
from quart_discord import requires_authorization, Unauthorized
from discord.ext.ipc import Client
import os 

from commons import loadFile, objectview
def request_bp(discord):

  config_pos = os.getenv('CONFIG_POS')
  cfg = loadFile(config_pos + "data.json")
  web_ipc = Client(secret_key=cfg["IPC_key"])
  request_c = Blueprint("request_c", __name__)

  @request_c.before_app_first_request
  async def before():
    request_c.ipc_node = await web_ipc.discover()


  @request_c.route("/api/get_guilds")
  async def getguilds():
    bot_guilds = objectview(await request_c.ipc_node.request("get_guilds"))
    #q_guilds = await discord.fetch_guilds()
    guildss = []

    #mal algoritmo. NECESITA CMABIOS.

#      for x in q_guilds:
    for c in bot_guilds:
#              if x.permissions.administrator and c.id == x.id:
      guildss.append({"id": str(c.id), "name": c.name})

    return jsonify(guildss)

  @request_c.route("/api/get_guild_info")
  async def get_info():

    guild = request.args.get("guild")
    if not guild: 
      return "", 400

    rols = []
    channs = []

    bot_guild_role = objectview(await request_c.ipc_node.request("get_guild_roles", eid=guild))
    for x in bot_guild_role:
        rols.append({"name": x.name,"id": str(x.id)})

    bot_guild_channels = objectview(await request_c.ipc_node.request("get_guild_channels", eid=guild))
    for x in bot_guild_channels:
        channs.append({"name": x.name,"id": str(x.id)})
    
    return jsonify({"channels": channs, "roles": rols})

  return request_c
