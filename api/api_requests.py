from quart import Blueprint, redirect, jsonify, request, url_for
from quart_discord import requires_authorization, Unauthorized
from discord.ext.ipc import Client
import os 
import random 
import psycopg2.extras

from oauthlib.oauth2.rfc6749.errors import TokenExpiredError, InvalidGrantError

from auth import has_access

from commons import loadFile, objectview, db_fetch, db_commit
def request_bp(discord, db):

    config_pos = os.getenv('CONFIG_POS')
    cfg = loadFile(config_pos + "data.json")
    web_ipc = Client(secret_key=cfg["IPC_key"])
    request_c = Blueprint("request_c", __name__)

    @request_c.before_app_first_request
    async def before():
        request_c.ipc_node = await web_ipc.discover()

    @request_c.route("/api/bot")
    async def getstats():
        dc = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        dc.execute("SELECT * FROM stats WHERE ts = 0")
        res = dc.fetchone()

        if res: 
            return jsonify({"users": res["users"], "guilds":res["guilds"], "msg": random.choice(cfg['useless'])})
        else: 
            return jsonify({"users":0, "guilds":0, "msg": "Uhmmmmmmmm, esto no está bien"})

    @request_c.route("/api/getGuilds")
    async def getguilds():

        if os.environ.get('DISABLE_AUTH') == 'True':
            bot_guilds = objectview(await request_c.ipc_node.request("get_guilds", user=str(254672103465418752)))

            guildss = []
            for c in bot_guilds:
                guildss.append({"id": str(c.id), "name": c.name})
        else:

            try: 
                Value = await discord.authorized
                if not Value: 
                    return False  

                user = await discord.fetch_user()
                uid = str(user.id)

                bot_guilds = objectview(await request_c.ipc_node.request("get_guilds", user=str(uid)))

            except (InvalidGrantError, TokenExpiredError):
                discord.revoke()
                return redirect("/api/login")

            dc = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
            dc.execute("DELETE FROM access WHERE id = %s", (uid, ))

            guildss = []
            for c in bot_guilds:
                guildss.append({"id": str(c.id), "name": c.name})
                dc.execute("INSERT INTO access(id, guild) VALUES(%s,%s)", (uid, c.id,))

            db.commit()
            dc.close()

        return jsonify(guildss)

    @request_c.route("/api/updateGuild", methods=["POST"])
    async def updateGuild():
        '''
        ''' 
        data = await request.get_json()
        try: 
            guild = str(data['guild'])
            props = data["data"]
        except: 
            return "", 400

        if not (await has_access(discord, guild, db)):
            return "", 401

        try: 
            prefix = str(props["prefix"])
        except: 
            return "", 400

        if len(prefix) > 6:
            return "", 400

        db_commit("UPDATE servidores SET prefix = %s WHERE guild = %s", (prefix, guild, ), db)

        return "", 200

    @request_c.route("/api/getGuildInfo")
    async def get_info():
        '''
        '''
        try:
            guild = str(request.args.get("guild"))
        except:
            return "", 400

        if not (await has_access(discord, guild, db)):
            return "", 401

        res = db_fetch("SELECT * FROM servidores WHERE guild=%s", (guild, ), db)

        if len(res) > 0: 
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

            db_commit("INSERT INTO servidores(guild, welcome, birthday, stalk, bdaymsg, bdayutc, type, prefix, levels) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,0)", (str(guild), 0, 0, 0, " ", 0, 0, "!", ), db)

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
