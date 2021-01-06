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

  @request_c.route("/api/bot")
  async def getstats():
    data = await db.execute("SELECT * FROM stats WHERE ts = 0")
    res = await data.fetchall()

    if res: 
      res = res[0]

      return jsonify({"users": res["users"], "guilds":res["guilds"]})

    return jsonify({"users":0, "guilds":0})
  @request_c.route("/api/getGuilds")
  async def getguilds():

    if os.environ.get('DISABLE_AUTH') == 'True':
      bot_guilds = objectview(await request_c.ipc_node.request("get_guilds", user=str(254672103465418752)))

      guildss = []
      for c in bot_guilds:
        guildss.append({"id": str(c.id), "name": c.name})

    else:

      Value = await discord.authorized
      if not Value: 
        return False  

      user = await discord.fetch_user()
      uid = user.id

      bot_guilds = objectview(await request_c.ipc_node.request("get_guilds", user=str(uid)))
      await dc.execute("DELETE FROM access WHERE id = ?", (uid, ))

      guildss = []
      for c in bot_guilds:
        guildss.append({"id": str(c.id), "name": c.name})
        await dc.execute("INSERT INTO access(id, guild) VALUES(?,?)", (uid, c.id,))

      await db.commit()

    return jsonify(guildss)

  @request_c.route("/api/updateGuild", methods=["POST"])
  async def updateGuild():
    '''
    ''' 
    data = await request.get_json()
    try: 
      guild = int(data['guild'])
      props = data["data"]
    except: 
      return "", 400

    if not (await has_access(discord, guild, dc)):
      return "", 401

    prefix = props["prefix"]
    if len(prefix) > 6:
      return "", 400

    await dc.execute("UPDATE servidores SET prefix = ? WHERE guild = ?", (prefix, guild, ))
    await db.commit()

    return "", 200

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
      prefix = str(res['prefix'])

      rols = []
      channs = []

      bot_guild_role = objectview(await request_c.ipc_node.request("get_guild_roles", eid=guild))
      for x in bot_guild_role:
          rols.append({"name": x.name,"id": str(x.id)})

      bot_guild_channels = objectview(await request_c.ipc_node.request("get_guild_channels", eid=guild))
      for x in bot_guild_channels:
          channs.append({"name": x.name,"id": str(x.id)})

      bot_guild_stats = await request_c.ipc_node.request("get_guild_stats", eid=guild)

      return jsonify({"channels": channs, 
                      "roles": rols,
                      "welcome": welcome,
                      "bday": cumple,
                      "stalk": stalk,
                      "tipo": tipo,
                      "prefix": prefix,
                      "stats": bot_guild_stats})

    else: 
      rols = []
      channs = []

      bot_guild_role = objectview(await request_c.ipc_node.request("get_guild_roles", eid=guild))
      for x in bot_guild_role:
          rols.append({"name": x.name,"id": str(x.id)})

      bot_guild_channels = objectview(await request_c.ipc_node.request("get_guild_channels", eid=guild))
      for x in bot_guild_channels:
          channs.append({"name": x.name,"id": str(x.id)})

      bot_guild_stats = await request_c.ipc_node.request("get_guild_stats", eid=guild)

      await dc.execute("INSERT INTO servidores(guild, welcome, birthday, stalk, bdaymsg, bdayutc, type, prefix) VALUES(?,?,?,?,?,?,?,?)", (guild, 0, 0, 0, " ", 0, 0, "!", ))
      await db.commit()

      return jsonify({"channels": channs, 
                      "roles": rols,
                      "welcome": 0,
                      "bday": 0,
                      "stalk": 0,
                      "tipo": 0,
                      "prefix": "!",
                      "stats": bot_guild_stats})

  @request_c.errorhandler(Unauthorized)
  async def redirect_unauthorized(e):
      return redirect("/api/login")

  return request_c
