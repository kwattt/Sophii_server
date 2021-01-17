from quart import Blueprint, redirect, jsonify, request, url_for
from quart_discord import requires_authorization, Unauthorized
import psycopg2.extras

from auth import has_access
from commons import db_fetch, db_commit

def levels_bp(discord, db):
    '''
    '''

    levels_c = Blueprint("levels_c", __name__)

    @levels_c.route("/api/levels")
    async def Levels():
        '''
        
        '''
        try:
            guild = request.args.get("guild")
        except:
            return "", 400

        if not (await has_access(discord, guild, db)):
            return "", 401
        
        levelsres = db_fetch("SELECT levels FROM servidores WHERE guild=%s", (guild, ), db)
        
        channels = db_fetch("SELECT * FROM levelchannel WHERE guild=%s", (guild, ), db)
        channelres = []
        for x in channels:
            channelres.append(channels["channel"])

        return jsonify({"enabled": levelsres[0]["levels"], "channels": channelres})


    @levels_c.route("/api/updateLevels", methods=["POST"])
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

        channels = props["channels"]

        dc = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        dc.execute("DELETE FROM levelchannel WHERE guild = %s", (guild,))

        for ch in channels:
            dc.execute('''INSERT INTO 
            levelchannel(guild, channel)
            VALUES(%s,%s)
            ''', (guild, ch,))

        db.commit()
        dc.close()

        db_commit("UPDATE servidores SET levels = %s WHERE guild = %s", (int(props["enabled"]), guild, ), db)

        return "", 200


    return levels_c