from quart import Blueprint, redirect, jsonify, request, url_for
from quart_discord import requires_authorization, Unauthorized

import aiosqlite

def msg_bp(discord, db, dc):

  msg_c = Blueprint("msg_c", __name__)

  @msg_c.route("/api/msg")
  async def Mensajes():
    guild = request.args.get("guild")
    if not guild: 
      return "", 400

    extraE = await db.execute("SELECT * FROM oraculo WHERE guild=?", (guild, ))
    extraD =  await extraE.fetchall()
    temp = []

    for msg in extraD:
        if msg:
            temp.append(msg["msg"])
    oraculo = ";\n".join(temp)

    return jsonify(oraculo)

  return msg_c