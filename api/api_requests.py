from quart import Blueprint, redirect, jsonify, request, url_for
from quart_discord import requires_authorization, Unauthorized
from discord.ext.ipc import Client
import os 

from auth import has_access


from commons import loadFile, objectview
def request_bp(discord, db, dc):

  config_pos = os.getenv('CONFIG_POS')
  cfg = loadFile(config_pos + "data.json")
  web_ipc = Client(secret_key=cfg["IPC_key"])
  request_c = Blueprint("request_c", __name__)

  @request_c.before_app_first_request
  async def before():
    request_c.ipc_node = await web_ipc.discover()


  @request_c.route("/api/getGuilds")
  async def getguilds():

    if os.environ.get('DISABLE_AUTH') == 'True':
      bot_guilds = objectview(await request_c.ipc_node.request("get_guilds"))

      guildss = []
      for c in bot_guilds:
        guildss.append({"id": str(c.id), "name": c.name})

    else:

      Value = await discord.authorized
      if not Value: 
        return False  

      user = await discord.fetch_user()
      uid = user.id

      bot_guilds = objectview(await request_c.ipc_node.request("get_guilds"))

      q_guilds = await discord.fetch_guilds()
      await dc.execute("DELETE FROM access WHERE id = ?", (uid, ))

      guildss = []
      for x in q_guilds:
        for c in bot_guilds:
          if x.permissions.administrator and c.id == x.id:
            guildss.append({"id": str(c.id), "name": c.name})
            await dc.execute("INSERT INTO access(id, guild) VALUES(?,?)", (uid, c.id,))

      await db.commit()

    return jsonify(guildss)

  @request_c.route("/api/getGuildInfo")
  async def get_info():
    '''
    '''

    guild = request.args.get("guild")
    if not guild: 
      return "", 400

    if not (await has_access(discord, guild, dc)):
      return "", 401

    data = await db.execute("SELECT * FROM servidores WHERE guild=?", (guild, ))
    res = await data.fetchall()

    if res: 
      res = res[0]

      welcome = str(res['welcome'])
      cumple = str(res['birthday'])
      stalk = str(res['stalk'])
      tipo = str(res['type'])

      rols = []
      channs = []

      bot_guild_role = objectview(await request_c.ipc_node.request("get_guild_roles", eid=guild))
      for x in bot_guild_role:
          rols.append({"name": x.name,"id": str(x.id)})

      bot_guild_channels = objectview(await request_c.ipc_node.request("get_guild_channels", eid=guild))
      for x in bot_guild_channels:
          channs.append({"name": x.name,"id": str(x.id)})
      
      return jsonify({"channels": channs, 
                      "roles": rols,
                      "welcome": welcome,
                      "bday": cumple,
                      "stalk": stalk,
                      "tipo": tipo})

    else: 
      rols = []
      channs = []

      bot_guild_role = objectview(await request_c.ipc_node.request("get_guild_roles", eid=guild))
      for x in bot_guild_role:
          rols.append({"name": x.name,"id": str(x.id)})

      bot_guild_channels = objectview(await request_c.ipc_node.request("get_guild_channels", eid=guild))
      for x in bot_guild_channels:
          channs.append({"name": x.name,"id": str(x.id)})
      

      await dc.execute("INSERT INTO servidores(guild, welcome, birthday, stalk, bdaymsg, bdayutc, type) VALUES(?,?,?,?,?,?,?)", (guild, 0, 0, 0, " ", 0, 0, ))

      return jsonify({"channels": channs, 
                      "roles": rols,
                      "welcome": 0,
                      "bday": 0,
                      "stalk": 0,
                      "tipo": 0})

  return request_c
