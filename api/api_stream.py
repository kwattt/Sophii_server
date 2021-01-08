from quart import Blueprint, redirect, jsonify, request, url_for
from quart_discord import requires_authorization, Unauthorized

import aiosqlite

from auth import has_access


def stream_bp(discord, db, dc):
  '''
  '''

  stream_c = Blueprint("stream_c", __name__)

  @stream_c.route("/api/updateSocial", methods=["POST"])
  async def updateStreams():
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

    tipod = await db.execute("SELECT type FROM servidores WHERE guild=?", (guild, ))
    tipo =  await tipod.fetchall()
    tipo = tipo[0][0]

    props = props["twitch"]

    if tipo == 0 and len(props) > 3:
      return "", 400 

    await dc.execute("DELETE FROM social WHERE guild = ?", (guild,))

    for st in props:
      if len(st["name"]) > 30:
        await db.rollback()
        return "", 400

      await dc.execute('''INSERT INTO 
      social(guild, name, platform, channel, type, live, last_update)
      VALUES(?,?,?,?,?,?,?)
      ''', (guild, st['name'], 'twitch', st['channel'], st['type'],0,0.0,))

    await db.commit()

    return "", 200

  @stream_c.route("/api/streams")
  #@requires_authorization
  async def Streams():
    '''
      
    '''

    guild = request.args.get("guild")
    if not guild: 
      return "", 400

    if not (await has_access(discord, guild, dc)):
      return "", 401

    twitchdata = await db.execute("SELECT * FROM social WHERE guild=?", (guild, ))
    twitchres =  await twitchdata.fetchall()

    twitch = []

    for x in twitchres:
      if x["platform"] == "twitch":
        twitch.append({"name": x["name"],"channel": str(x["channel"]),"type": str(x["type"])}) 

    return jsonify({"twitch": twitch})


  return stream_c
