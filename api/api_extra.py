from quart import Blueprint, redirect, jsonify, request, url_for
from quart_discord import requires_authorization, Unauthorized

import aiosqlite

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

    if "bday" in props:
      
      bday = props["bday"]
      bdaymsg = props["bdaymsg"]
      bdayutc = props["bdayutc"]

      try:
          bdaymsg.format(123)
      except IndexError:
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

      await dc.execute("DELETE from stalkmsg WHERE guild=?", (guild,))

      values = msgs.replace("\n", "").split(";")
      for msg in values:
          if msg:
              await dc.execute("INSERT INTO stalkmsg(guild,msg) VALUES(?,?)", (guild,msg.lstrip(),))

    await db.commit()

    return "", 200


  @extra_c.route("/api/extra")
  async def Stalk():

    guild = request.args.get("guild")
    if not guild: 
      return "", 400

    datad = await dc.execute("SELECT stalk, bdaymsg, birthday, bdayutc FROM servidores WHERE guild=?", (guild, ))
    data =  await datad.fetchall() 
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

    if not bday:
      bday = "{}"

    return jsonify({"role": stalk_roles, 
                    "msg": stalk_msg,
                    "bday": bday,
                    "stalk": stalk,
                    "bdaymsg": bdaymsg,
                    "bdayutc": bdayutc})

  return extra_c