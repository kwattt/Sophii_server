from quart import Blueprint, redirect, jsonify, request, url_for
from quart_discord import requires_authorization, Unauthorized
import psycopg2.extras

from datetime import datetime

from auth import has_access
from commons import db_fetch, db_commit

def social_bp(discord, db):
    '''
    '''

    social_c = Blueprint("social_c", __name__)

    @social_c.route("/api/updateSocial", methods=["POST"])
    async def updateSocial():
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

        if "twitter" in props:
            props = props["twitter"]
            if tipo == 0 and len(props) > 5:
                return "", 400 

            dc = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
            dc.execute("DELETE FROM social WHERE guild = %s AND platform = 'twitter'", (guild,))

            for st in props:
                if len(st["name"]) > 30:
                    db.rollback()
                    dc.close()
                    return "", 400

                dc.execute('''INSERT INTO 
                social(guild, name, platform, channel, type, live, last_update)
                VALUES(%s,%s,%s,%s,%s,%s,%s)
                ''', (guild, st['name'], 'twitter', str(st['channel']), st['type'], 0, str(0),))

            db.commit()
            dc.close()


        if "facebook" in props:
            props = props["facebook"]

            if tipo == 0 and len(props) > 5:
                return "", 400 

            dc = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
            dc.execute("DELETE FROM social WHERE guild = %s AND platform = 'facebook'", (guild,))

            for st in props:
                if len(st["name"]) > 200:
                    db.rollback()
                    dc.close()
                    return "", 400

                dc.execute('''INSERT INTO 
                social(guild, name, platform, channel, type, live, last_update)
                VALUES(%s,%s,%s,%s,%s,%s,%s)
                ''', (guild, st['name'], 'facebook', str(st['channel']), st['type'], 0, str(0),))

            db.commit()
            dc.close()

        if "twitch" in props:
            props = props["twitch"]

            if tipo == 0 and len(props) > 4:
                return "", 400 

            dc = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
            dc.execute("DELETE FROM social WHERE guild = %s AND platform = 'twitch'", (guild,))

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

    @social_c.route("/api/social")
    async def Social():
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
        facebook = []
        twitter = []
        for x in twitchres:
            if x["platform"] == "twitch":
                twitch.append({"name": x["name"],"channel": str(x["channel"]),"type": str(x["type"])}) 
            if x["platform"] == "youtube":
                youtube.append({"name": x["name"],"channel": str(x["channel"]),"type": str(x["type"])}) 
            if x["platform"] == "facebook":
                facebook.append({"name": x["name"],"channel": str(x["channel"]),"type": str(x["type"])}) 
            if x["platform"] == "twitter":
                twitter.append({"name": x["name"],"channel": str(x["channel"]),"type": str(x["type"])}) 
            
        return jsonify({"twitter": twitter, "twitch": twitch, "youtube": youtube, "facebook": facebook})


    return social_c
