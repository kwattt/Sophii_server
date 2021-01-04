from quart import Blueprint, redirect, jsonify, request, url_for
from quart_discord import requires_authorization, Unauthorized

import aiosqlite

def msg_bp(discord, db, dc):

  msg_c = Blueprint("msg_c", __name__)

  @msg_c.route("/api/updateMsg", methods=["POST"])
  async def updateMensajes():

    data = await request.get_json()
    try: 
      guild = int(data['guild'])
      props = data["data"]
    except: 
      return "", 400

    if "channel" in props:
      channel = props["channel"]
      
      if(len(channel) > 25):
        return "", 400

      await dc.execute("UPDATE servidores SET welcome = ? WHERE guild = ?", (channel, guild, ))

    if "join" in props:
      join = props["join"]
      ent = join.replace("\n", "").split(";")

      if len(join) > 1500:
        return "", 400


      for msg in ent:
          try:
              msg.format(123)
          except IndexError:
              return "", 400

      await dc.execute("DELETE from WELCOME WHERE guild=? AND tipo=0", (guild,))
    
      for msg in ent:
          if msg:
              await dc.execute("INSERT INTO welcome(guild,tipo,msg) VALUES(?,?,?)", (guild,0,msg.lstrip(),))

    if "leave" in props:
      leave = props["leave"]

      if len(leave) > 1500:
        return "", 400

      sal = leave.replace("\n", "").split(";")

      for msg in sal:
          try:
              msg.format(123)
          except IndexError:
              return "", 400

      await dc.execute("DELETE from WELCOME WHERE guild=? AND tipo=1", (guild,))

      for msg in sal:
          if msg:
              await dc.execute("INSERT INTO welcome(guild,tipo,msg) VALUES(?,?,?)", (guild,1,msg.lstrip(),))

    if "oraculo" in props:
      oraculo = props["oraculo"]

      if len(oraculo) > 1500:
        return "", 400

      oraculo = oraculo.replace("\n", "").split(";")

      for msg in oraculo:
          try:
              msg.format(123)
          except IndexError:
              return "", 400

      await dc.execute("DELETE from oraculo WHERE guild=?", (guild,))

      for msg in oraculo:
          if msg:
              await dc.execute("INSERT INTO oraculo(guild,msg) VALUES(?,?)", (guild,msg.lstrip(),))

    await db.commit()

    return "", 200

  @msg_c.route("/api/msg")
  async def Mensajes():
    guild = request.args.get("guild")
    if not guild: 
      return "", 400

    datad = await db.execute("SELECT welcome FROM servidores WHERE guild=?", (guild, ))
    data = await datad.fetchall()
    welcome = str(data[0][0])

    extraE = await db.execute("SELECT * FROM oraculo WHERE guild=?", (guild, ))
    extraD =  await extraE.fetchall()
    temp = []

    for msg in extraD:
        if msg:
            temp.append(msg["msg"])
    oraculo = ";\n\n".join(temp)

    welcomemsg = await db.execute("SELECT * FROM welcome WHERE guild=?", (guild, ))
    welcomeres =  await welcomemsg.fetchall()

    ent = []
    sal = []
    for msg in welcomeres:
        if msg["tipo"] == 0:
            ent.append(msg["msg"])
        else:
            sal.append(msg["msg"])
    ent = ";\n\n".join(ent)
    sal = ";\n\n".join(sal)

    return jsonify({"channel":welcome, 
                    "oraculo": oraculo, 
                    "join": ent, 
                    "leave": sal})

  return msg_c