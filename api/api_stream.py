from quart import Blueprint, redirect, jsonify, request, url_for
from quart_discord import requires_authorization, Unauthorized
import psycopg2.extras

from auth import has_access
from commons import db_fetch, db_commit

def stream_bp(discord, db):
    '''
    '''

    stream_c = Blueprint("stream_c", __name__)

    @stream_c.route("/api/updateSocial", methods=["POST"])
    async def updateStreams():
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

        tipo = db_fetch("SELECT type FROM servidores WHERE guild=%s", (guild, ), db)
        tipo = tipo[0]["type"]
        
        if "twitch" in props:
            props = props["twitch"]

            if tipo == 0 and len(props) > 3:
                return "", 400 

            dc = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
            dc.execute("DELETE FROM social WHERE guild = %s", (guild,))

            for st in props:
                if len(st["name"]) > 30:
                    db.rollback()
                    dc.close()
                    return "", 400

                dc.execute('''INSERT INTO 
                social(guild, name, platform, channel, type, live, last_update)
                VALUES(%s,%s,%s,%s,%s,%s,%s)
                ''', (guild, st['name'], 'twitch', str(st['channel']), st['type'], 0, 0,))

            db.commit()
            dc.close()

        return "", 200

    @stream_c.route("/api/streams")
    async def Streams():
        '''
        
        '''
        try:
            guild = request.args.get("guild")
        except:
            return "", 400

        if not (await has_access(discord, guild, db)):
            return "", 401

        twitchres = db_fetch("SELECT * FROM social WHERE guild=%s", (guild, ), db)

        twitch = []
        youtube = []
        for x in twitchres:
            if x["platform"] == "twitch":
                twitch.append({"name": x["name"],"channel": str(x["channel"]),"type": str(x["type"])}) 
            if x["platform"] == "youtube":
                youtube.append({"name": x["name"],"channel": str(x["channel"]),"type": str(x["type"])}) 
            
        return jsonify({"twitch": twitch, "youtube": youtube})


    return stream_c
