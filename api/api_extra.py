from quart import Blueprint, redirect, jsonify, request, url_for
from quart_discord import requires_authorization, Unauthorized

import aiosqlite

from auth import has_access

def extra_bp(discord, db, dc):

  extra_c = Blueprint("extra_c", __name__)

  @extra_c.route("/api/updateExtra", methods=["POST"])
  async def updateExtra():

    data = await request.get_json()
    try: 
      guild = int(data['guild'])
      props = data["data"]
    except: 
      return "", 400

    if not (await has_access(discord, guild, dc)):
      return "", 401

    if "bday" in props:

      bday = props["bday"]
      bdaymsg = props["bdaymsg"]

      try: 
        bdayutc = int(props["bdayutc"])
      except:
        return "", 400

      try:
          bdaymsg.format(123)
      except IndexError:
          return "", 400


      if len(bdaymsg) > 350:
        return "", 400

      await dc.execute("UPDATE servidores SET birthday = ?, bdaymsg = ?, bdayutc = ? WHERE guild = ?", (bday, bdaymsg, bdayutc, guild, ))

    if "role" in props:

      stalk = props["stalk"]
      role = props["role"]

      await dc.execute("UPDATE servidores SET stalk = ? WHERE guild = ?", (stalk, guild, ))
      await dc.execute("DELETE FROM stalkroles WHERE guild = ?", (guild,))

      for rol in role:
        await dc.execute("INSERT INTO stalkroles(guild, role) VALUES(?,?)", (guild, rol,))

    if "msg" in props:

      msgs = props["msg"]

      if len(msgs) > 1000:
        return "", 400

      await dc.execute("DELETE from stalkmsg WHERE guild=?", (guild,))

      values = msgs.replace("\n", "").split(";")
      for msg in values:
          if msg:
              await dc.execute("INSERT INTO stalkmsg(guild,msg) VALUES(?,?)", (guild,msg.lstrip(),))

    await db.commit()

    return "", 200

  @extra_c.route("/api/extra")
  async def Extra():

    guild = request.args.get("guild")
    if not guild: 
      return "", 400

    if not (await has_access(discord, guild, dc)):
      return "", 401

    datad = await dc.execute("SELECT stalk, bdaymsg, birthday, bdayutc FROM servidores WHERE guild=?", (guild, ))
    data =  await datad.fetchall() 

    if not data:
      return "", 400

    data = data[0]

    stalk = data["stalk"]
    bdaymsg = data["bdaymsg"]
    bday = data["birthday"]
    bdayutc = data["bdayutc"]

    stalkdata = await dc.execute("SELECT * FROM stalkmsg WHERE guild=?", (guild, ))
    stalkres =  await stalkdata.fetchall()
    temp = []
    for x in stalkres:
        temp.append(x["msg"])
    temp = ";\n".join(temp)
    stalk_msg = temp 

    temp = []
    stalkdata = await dc.execute("SELECT * FROM stalkroles WHERE guild=?", (guild, ))
    stalkres =  await stalkdata.fetchall()
    for x in stalkres:
        temp.append(str(x["role"]))
    stalk_roles = temp

    return jsonify({"role": stalk_roles, 
                    "msg": stalk_msg,
                    "bday": bday,
                    "stalk": stalk,
                    "bdaymsg": bdaymsg,
                    "bdayutc": bdayutc})


  @extra_c.route("/api/updatePurge", methods=["POST"])
  async def updatePurge():

    data = await request.get_json()
    try: 
      guild = int(data['guild'])
      props = data["data"]
    except: 
      return "", 400

    if not (await has_access(discord, guild, dc)):
      return "", 401

    await dc.execute("DELETE FROM purge WHERE guild = ?", (guild, ))

    for x in props:
      try: 
        canal = x["channel"]
        hora = int(x["hour"]) 
        minuto = int(x["minute"])
        utc = int(x["utc"])
      except:
        return "", 400

      await dc.execute("INSERT INTO purge(guild, channel, hour, minute, utc) VALUES(?,?,?,?,?)", (guild, canal, hora, minuto, utc,))

    await db.commit()

    return "", 200

  @extra_c.route("/api/purge")
  #@requires_authorization
  async def Streams():
    '''

    '''

    guild = request.args.get("guild")
    if not guild: 
      return "", 400

    if not (await has_access(discord, guild, dc)):
      return "", 401

    datad = await dc.execute("SELECT * FROM purge WHERE guild=?", (guild, ))
    res =  await datad.fetchall()

    purge = []

    for x in res:
      purge.append({
        "channel": str(x["channel"]),
        "hour": x["hour"], 
        "minute": x["minute"], 
        "utc": x["utc"]}) 

    return jsonify(purge)


  return extra_c