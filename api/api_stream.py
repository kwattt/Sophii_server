from quart import Blueprint, redirect, jsonify, request, url_for
from quart_discord import requires_authorization, Unauthorized

import aiosqlite

def stream_bp(discord, db, dc):
  '''
  '''

  stream_c = Blueprint("stream_c", __name__)

  @stream_c.errorhandler(Unauthorized)
  async def redirect_unauthorized(e):
      return redirect("/api/login")

  @stream_c.route("/api/updateSocial", methods=["POST"])
  async def updateStreams():
    '''
    '''

    data = await request.get_json()
    print(data)
    try: 
      guild = int(data['guild'])
      props = data["data"]
    except: 
      return "", 400

    # delete old data

    await dc.execute("DELETE FROM social WHERE guild = ?", (guild,))

    props = props["twitch"]
    for st in props:
      
      await dc.execute('''INSERT INTO 
      social(guild, name, platform, channel, type)
      VALUES(?,?,?,?,?)
      ''', (guild, st['name'], 'twitch', st['channel'], st['type']))

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

    twitchdata = await db.execute("SELECT * FROM social WHERE guild=?", (guild, ))
    twitchres =  await twitchdata.fetchall()

    twitch = []

    for x in twitchres:
      if x["platform"] == "twitch":
        twitch.append({"name": x["name"],"channel": str(x["channel"]),"type": str(x["type"])}) 

    return jsonify({"twitch": twitch})

  return stream_c
