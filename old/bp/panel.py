from quart_discord import requires_authorization, Unauthorized
from functools import partial, wraps
from discord.ext import commands
from discord.ext.ipc import Client
from quart import Blueprint, jsonify, render_template, redirect, url_for, request
from commons import loadFile, objectview
from wsite import discords as discord
import json
import aiosqlite


cfg = loadFile("../config/data.json")
panel = Blueprint("panel", __name__,static_folder="/static/", template_folder="/templates/")
web_ipc = Client(secret_key=cfg["IPC_key"])

dbase = None
d_base = None

async def before():
    global dbase, d_base
    dbase = await aiosqlite.connect('../config/test.db')
    dbase.row_factory = aiosqlite.Row
    d_base = await dbase.cursor()

    panel.ipc_node = await web_ipc.discover()
panel.before_request(before)

@panel.route('/panel/')
@requires_authorization
async def panels():
    guildss = []
    bot_guilds = objectview(await panel.ipc_node.request("get_guilds"))

    q_guilds = await discord.fetch_guilds()

    for x in q_guilds:
        for c in bot_guilds:

            if x.permissions.administrator and c.id == x.id:
                guildss.append({"id": str(x.id), "name": x.name})

    return await render_template("panel.vue", guildss=guildss, twitchInfo=None, xd='LOL')

@panel.route('/callback/')
async def callback():
    data = await discord.callback()
    redirect_to = data.get("redirect", "/panel/")
    return redirect(redirect_to)

async def checkGuild(gid):
    data = await d_base.execute("SELECT welcome FROM servidores WHERE guild=?", (gid,))
    res = await data.fetchall()
    
    if not res:
        await d_base.execute("INSERT INTO servidores(guild, welcome, birthday, stalk) VALUES(?,?,?,?)", (gid,0,0,0.0,))
        await dbase.commit()

@panel.route("/updateExtra", methods=['POST'])
@requires_authorization
async def updateExtra():
    val = await request.get_json()
    try:
        gid = int(val["guild"])
        cumple = int(val['cumple'])
        oraculo = val['oraculo']
    except:
        return jsonify({"badData": True})

    await d_base.execute("UPDATE servidores SET birthday = ? WHERE guild = ?", (cumple, gid,))

    await d_base.execute("DELETE from oraculo WHERE guild=?", (gid,))

    msgs = oraculo.replace("\n", "").split(";")
    for msg in msgs:
        if msg:
            await d_base.execute("INSERT INTO oraculo(guild,msg) VALUES(?,?)", (gid,msg,))

    await dbase.commit()
    return jsonify({"badData": False})


@panel.route("/updateStalk", methods=['POST'])
@requires_authorization
async def updateStalk():
    val = await request.get_json()
    try:
        gid = int(val["guild"])
        stalk = val["stalk"]
    except:
        return jsonify({"badData": True})

    # MORE CHECKS my dude!

    stalkval = int(stalk['value'])
    if stalkval > 100 or stalkval < 0:
        return jsonify({"badData": True})

    await d_base.execute("UPDATE servidores SET stalk = ? WHERE guild = ?", (stalkval, gid,))

    print(gid, stalkval)

    await d_base.execute("DELETE from stalkroles WHERE guild=?", (gid,))
    for role in stalk['roles']:
        try:
            await d_base.execute("INSERT INTO stalkroles(guild,role) VALUES(?,?)", (gid,int(role),))
        except:
            pass

    await d_base.execute("DELETE from stalkmsg WHERE guild=?", (gid,))
    msgs = stalk["msg"].replace("\n", "").split(";")
    for msg in msgs:
        if msg:
            await d_base.execute("INSERT INTO stalkmsg(guild,msg) VALUES(?,?)", (gid,msg,))

    await dbase.commit()

    return jsonify({"badData": False})


@panel.route("/updateDoor", methods=['POST'])
@requires_authorization
async def updateDoor():
    val = await request.get_json()
    try:
        gid = int(val["guild"])
        door = val["door"]
    except:
        return "Bad Request", 400

    # msgs entrada

    await d_base.execute("UPDATE servidores SET welcome = ? WHERE guild = ?", (door["channel"], gid,))

    ent = door["enter"].replace("\n", "").split(";")
    sal = door["exit"].replace("\n", "").split(";")

    for msg in ent:
        try:
            msg.format(123)
        except IndexError:
            return jsonify({"badData": True})

    for msg in sal:
        try:
            msg.format(123)
        except IndexError:
            return jsonify({"badData": True})

    await d_base.execute("DELETE from WELCOME WHERE guild=?", (gid,))

    for msg in ent:
        if msg:
            await d_base.execute("INSERT INTO welcome(guild,tipo,msg) VALUES(?,?,?)", (gid,0,msg,))

    for msg in sal:
        if msg:
            await d_base.execute("INSERT INTO welcome(guild,tipo,msg) VALUES(?,?,?)", (gid,1,msg,))
    await dbase.commit()

    return jsonify({"badData": False})

@panel.route("/updateSocial", methods=['POST'])
@requires_authorization
async def updateSocial():
    val = await request.get_json()
    try:
        gid = int(val["guild"])
        streams = val["streams"]
    except:
        return "Bad Request", 400
    
    # NEED MORE CHECKS!

    await d_base.execute("DELETE from social WHERE guild=?", (gid,))

    for current in streams:
        if current["name"] != "Nuevo":
            await d_base.execute("INSERT INTO social(guild,platform,channel,name,last_update,live,type) VALUES(?,?,?,?,?,?,?)", (gid,"twitch",current["channel"],current["name"],0.0,0,current["type"],))
    await dbase.commit()

    return "all good my man", 200

@panel.route("/setGuild", methods=['POST'])
@requires_authorization
async def setGuild():
    val = await request.get_json()
    gid = int(val['guild'])

    if (await has_server_perm(gid)):

        data = await d_base.execute("SELECT * FROM servidores WHERE guild=?", (gid, ))
        res = await data.fetchall()
     
        if res:
            res = res[0]

            welcome = str(res['welcome'])
            cumple = str(res['birthday'])
            twitchs = []
            rols = []
            channs = []
            stalk = {"value": res['stalk'], "roles": [], "msg": ""}

            stalkdata = await dbase.execute("SELECT * FROM stalkmsg WHERE guild=?", (gid, ))
            stalkres =  await stalkdata.fetchall()
            temp = []
            for x in stalkres:
                temp.append(x["msg"])
            temp = ";\n".join(temp)
            stalk['msg'] = temp 

            temp = []
            stalkdata = await dbase.execute("SELECT * FROM stalkroles WHERE guild=?", (gid, ))
            stalkres =  await stalkdata.fetchall()
            for x in stalkres:
                temp.append(x["role"])
            stalk['roles'] = temp

            twitchdata = await dbase.execute("SELECT * FROM social WHERE guild=?", (gid, ))
            twitchres =  await twitchdata.fetchall()

            for x in twitchres:
                if x["platform"] == "twitch":
                    twitchs.append({"name": x["name"],"channel": str(x["channel"]),"type": x["type"]})                    

            bot_guild_role = objectview(await panel.ipc_node.request("get_guild_roles", eid=gid))
            for x in bot_guild_role:
                rols.append({"name": x.name,"id": str(x.id)})

            bot_guild_channels = objectview(await panel.ipc_node.request("get_guild_channels", eid=gid))
            for x in bot_guild_channels:
                channs.append({"name": x.name,"id": str(x.id)})

            welcomemsg = await dbase.execute("SELECT * FROM welcome WHERE guild=?", (gid, ))
            welcomeres =  await welcomemsg.fetchall()

            ent = []
            sal = []
            for msg in welcomeres:
                if msg["tipo"] == 0:
                    ent.append(msg["msg"])
                else:
                    sal.append(msg["msg"])
            ent = ";\n".join(ent)
            sal = ";\n".join(sal)
            welcomeres = {"enter": ent, "exit": sal}
            welcomeres["channel"] = str(welcome)

            extraE = await dbase.execute("SELECT * FROM oraculo WHERE guild=?", (gid, ))
            extraD =  await extraE.fetchall()
            temp = []
            for msg in extraD:
                if msg:
                    temp.append(msg["msg"])

            oraculo = ";\n".join(temp)

            return jsonify(
                {'twitch': twitchs,
                 'channels': channs,
                 'roles': rols,
                 'welcome': welcome,
                 'door': welcomeres,
                 'stalk': stalk,
                 'cumple': cumple,
                 'oraculo': oraculo
                 })
        else:
            await checkGuild(gid)
            ## NEED CHANGES AND THE FUNC TOO
            return "guild in a sec", 500
    return "", 500

@panel.route('/login/') 
async def login():
    return await discord.create_session(scope=["guilds", "identify"])

@panel.errorhandler(Unauthorized)
async def redirect_unauthorized(e):
    return redirect(url_for("panel.login"))

async def has_server_perm(serverid):
    d_guilds = await discord.fetch_guilds()
    for x in d_guilds:
        if x.permissions.administrator and x.id == serverid:
            return True
    return False
