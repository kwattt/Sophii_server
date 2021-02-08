from quart import Blueprint, redirect, jsonify, request, url_for
from quart_discord import requires_authorization, Unauthorized
import psycopg2.extras

import os
import googleapiclient.discovery

api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = os.environ.get('youtube')

youtube = googleapiclient.discovery.build(
api_service_name, api_version, developerKey = DEVELOPER_KEY)


from datetime import datetime

from auth import has_access
from commons import db_fetch, db_commit

def social_bp(discord, db):
    '''
    '''

    social_c = Blueprint("social_c", __name__)

    async def getChannelUploadPlaylistAndName(channelId):
            request = youtube.channels().list(
                    part="contentDetails,snippet",
                    id=channelId
            )
            response = request.execute()

            if "items" in response:
                    vals = response["items"][0]
                    return vals['snippet']['title'], vals["contentDetails"]["relatedPlaylists"]["uploads"]
            else:
                    return None, None

    async def getLastetsVideoDate(playlistId):
            if playlistId == None:
                return None
            request = youtube.playlistItems().list(
            part="snippet,contentDetails",
            maxResults=1,
            playlistId=playlistId
            )
            response = request.execute()

            if "items" in response:
                for x in response["items"]:
                    return x["contentDetails"]["videoId"] 
            else: 
                return None 

    @social_c.route("/api/verifyChannel", methods=["POST"])
    async def verifyYoutubeChannel():
        data = await request.get_json()
        try: 
            guild = str(data['guild'])
            props = data["data"]
        except: 
            return "", 400

        if "channelId" in props:
            channelName, __ = await getChannelUploadPlaylistAndName(props["channelId"])

            if not channelName:
                return "", 400
            else:
                return jsonify({"channelName": channelName})
        else:
            return "", 400 

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

        if "youtube" in props:
            props = props["youtube"]
            if tipo == 0 and len(props) > 3:
                return "", 400 

            dc = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
            current_platform = db_fetch("SELECT id FROM social WHERE guild = %s AND platform = 'youtube'", (guild,) ,db) 
            ids = [int(x["id"]) for x in current_platform]

            for current in props:
                try:
                    name = str(current["name"])
                    cid = int(current["id"])
                    channel = str(current["channel"])
                    ctype = int(current["type"])
                    channel_name = str(current["channel_name"])
                except:
                    db.rollback()
                    dc.close()
                    return "", 400

                if len(name) > 200 or len(channel_name) > 200 :
                    db.rollback()
                    dc.close()
                    return "", 400

                if cid == -1:
                    dc.execute('''
                    INSERT INTO 
                    social(guild, platform, channel, name, last_update, live, type, real_name)
                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
                    ''',
                    (guild, "youtube", channel, name, "0", 0, ctype, channel_name,))
                elif cid in ids:
                    db_commit("UPDATE social SET channel = %s, name = %s, type = %s, real_name = %s WHERE id = %s AND guild = %s", (channel, name, ctype, channel_name, cid, guild,), db)

                if cid != -1:
                    ids.remove(cid)

            for cid in ids:
                dc.execute("DELETE FROM social WHERE id = %s AND guild = %s", (cid, guild, ))

            db.commit()
            dc.close()

        if "twitter" in props:
            props = props["twitter"]
            if tipo == 0 and len(props) > 5:
                return "", 400 

            dc = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
            current_platform = db_fetch("SELECT id FROM social WHERE guild = %s AND platform = 'twitter'", (guild,) ,db) 
            ids = [int(x["id"]) for x in current_platform]

            for current in props:
                try:
                    name = str(current["name"])
                    cid = int(current["id"])
                    channel = str(current["channel"])
                    ctype = int(current["type"])
                except:
                    db.rollback()
                    dc.close()
                    return "", 400

                if len(name) > 200:
                    db.rollback()
                    dc.close()
                    return "", 400

                if cid == -1:
                    dc.execute('''
                    INSERT INTO 
                    social(guild, name, platform, channel, type, live, last_update)
                    VALUES(%s,%s,%s,%s,%s,%s,%s)
                    ''',
                    (guild, name, "twitter", channel, ctype, 0, "0",))
                elif cid in ids:
                    db_commit("UPDATE social SET channel = %s, name = %s, type = %s WHERE id = %s AND guild = %s", (channel, name, ctype, cid, guild,), db)

                if cid != -1:
                    ids.remove(cid)

            for cid in ids:
                dc.execute("DELETE FROM social WHERE id = %s AND guild = %s", (cid, guild, ))

            db.commit()
            dc.close()

        if "facebook" in props:
            props = props["facebook"]

            if tipo == 0 and len(props) > 5:
                return "", 400 

            dc = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
            current_platform = db_fetch("SELECT id FROM social WHERE guild = %s AND platform = 'facebook'", (guild,) ,db) 

            ids = [int(x["id"]) for x in current_platform]

            for current in props:
                try:
                    name = str(current["name"])
                    cid = int(current["id"])
                    channel = str(current["channel"])
                    ctype = int(current["type"])
                except:
                    db.rollback()
                    dc.close()
                    return "", 400

                if len(name) > 200:
                    db.rollback()
                    dc.close()
                    return "", 400

                if cid == -1:
                    dc.execute('''
                    INSERT INTO 
                    social(guild, name, platform, channel, type, live, last_update)
                    VALUES(%s,%s,%s,%s,%s,%s,%s)
                    ''',
                    (guild, name, "facebook", channel, ctype, 0, "0",))
                elif cid in ids:
                    db_commit("UPDATE social SET channel = %s, name = %s, type = %s WHERE id = %s AND guild = %s", (channel, name, ctype, cid, guild,), db)

                if cid != -1:
                    ids.remove(cid)

            for cid in ids:
                dc.execute("DELETE FROM social WHERE id = %s AND guild = %s", (cid, guild, ))

            db.commit()
            dc.close()

        if "twitch" in props:
            props = props["twitch"]

            if tipo == 0 and len(props) > 4:
                return "", 400 

            dc = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
            current_platform = db_fetch("SELECT id FROM social WHERE guild = %s AND platform = 'twitch'", (guild,) ,db) 

            ids = [int(x["id"]) for x in current_platform]

            for current in props:
                try:
                    name = str(current["name"])
                    cid = int(current["id"])
                    channel = str(current["channel"])
                    ctype = int(current["type"])
                except:
                    db.rollback()
                    dc.close()
                    return "", 400

                if len(name) > 200:
                    db.rollback()
                    dc.close()
                    return "", 400

                if cid == -1:
                    dc.execute('''
                    INSERT INTO 
                    social(guild, name, platform, channel, type, live, last_update)
                    VALUES(%s,%s,%s,%s,%s,%s,%s)
                    ''',
                    (guild, name, "twitch", channel, ctype, 0, "0",))
                elif cid in ids:
                    db_commit("UPDATE social SET channel = %s, name = %s, type = %s WHERE id = %s AND guild = %s", (channel, name, ctype, cid, guild,), db)

                if cid != -1:
                    ids.remove(cid)

            for cid in ids:
                dc.execute("DELETE FROM social WHERE id = %s AND guild = %s", (cid, guild, ))

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
                twitch.append({"id": x["id"], "name": x["name"],"channel": str(x["channel"]),"type": str(x["type"])}) 
            if x["platform"] == "youtube":
                youtube.append({"id": x["id"], "name": x["name"], "channel_name": x["real_name"], "channel": str(x["channel"]),"type": str(x["type"])}) 
            if x["platform"] == "facebook":
                facebook.append({"id": x["id"], "name": x["name"],"channel": str(x["channel"]),"type": str(x["type"])}) 
            if x["platform"] == "twitter":
                twitter.append({"id": x["id"], "name": x["name"],"channel": str(x["channel"]),"type": str(x["type"])}) 
        return jsonify({"twitter": twitter, "twitch": twitch, "youtube": youtube, "facebook": facebook})


    return social_c
