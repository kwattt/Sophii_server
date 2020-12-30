from quart import Blueprint, redirect, jsonify, request, url_for
from quart_discord import requires_authorization, Unauthorized

import aiosqlite

def extra_bp(discord, db, dc):

  extra_c = Blueprint("extra_c", __name__)

  @extra_c.route("/api/extra")
  async def Stalk():

    guild = request.args.get("guild")
    if not guild: 
      return "", 400

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
    
    return jsonify({"role": stalk_roles, "msg": stalk_msg})

  return extra_c