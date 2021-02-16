from quart import Blueprint, jsonify, request
import psycopg2.extras

from auth import has_access
from commons import  db_fetch

def extra2_bp(discord, db):

    extra_c2 = Blueprint("extra_c2", __name__)

    @extra_c2.route("/api/updatePurge", methods=["POST"])
    async def updatePurge():

        data = await request.get_json()
        try: 
            guild = str(data['guild'])
            props = list(data["data"])
        except: 
            return "", 400

        if not (await has_access(discord, guild, db)):
            return "", 401

        if len(props > 5):
            return "", 400

        dc = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        dc.execute("DELETE FROM purge WHERE guild = %s", (guild, ))

        for x in props:
            try: 
                canal = str(x["channel"])
                hora = int(x["hour"]) 
                minuto = int(x["minute"])
                utc = int(x["utc"])
            except:
                db.rollback()
                dc.close()
                return "", 400

            if (hora < 0 or hora > 23 or
                minuto < 0 or minuto > 59 or
                utc < -12 or utc > 14):

                db.rollback()
                dc.close()
                return "", 400

            dc.execute("INSERT INTO purge(guild, channel, hour, minute, utc) VALUES(%s,%s,%s,%s,%s)", (guild, canal, hora, minuto, utc,))

        db.commit()
        dc.close()

        return "", 200

    @extra_c2.route("/api/updateAutochannel", methods=["POST"])
    async def updateAuto():

        data = await request.get_json()
        try: 
            guild = str(data['guild'])
            props = list(data["data"])
        except: 
            return "", 400

        if not (await has_access(discord, guild, db)):
            return "", 401

        if len(props) > 6:
            return "", 400

        dc = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        dc.execute("DELETE FROM autochannel WHERE guild = %s", (guild, ))

        for x in props:
            try: 
                origen = str(x["origen"])
                target = str(x["target"]) 
            except:
                db.rollback()
                dc.close()
                return "", 400

            dc.execute("INSERT INTO autochannel(guild, origenchannel, targetchannel) VALUES(%s,%s,%s)", (guild, origen, target,))

        db.commit()
        dc.close()

        return "", 200

    @extra_c2.route("/api/autochannel")
    async def AutoChannel():
        '''
        '''

        try:
            guild = str(request.args.get("guild"))
        except:
            return "", 400

        if not (await has_access(discord, guild, db)):
            return "", 401

        res = db_fetch("SELECT * FROM autochannel WHERE guild=%s", (guild, ), db)

        autochannel = []

        for x in res: 
            autochannel.append({
                "id": x["id"], 
                "origen": x["origenchannel"], 
                "target": x["targetchannel"]}) 

        return jsonify(autochannel)

    @extra_c2.route("/api/purge")
    async def Streams():
        '''

        '''
        try:
            guild = str(request.args.get("guild"))
        except:
            return "", 400

        if not (await has_access(discord, guild, db)):
            return "", 401

        res = db_fetch("SELECT * FROM purge WHERE guild=%s", (guild, ), db)

        purge = []

        for x in res:
            purge.append({
                "channel": str(x["channel"]),
                "hour": x["hour"], 
                "minute": x["minute"], 
                "utc": x["utc"]}) 

        return jsonify(purge)

    return extra_c2