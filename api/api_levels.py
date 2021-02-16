from quart import Blueprint, jsonify, request
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
            channelres.append(x["channel"])

        store = db_fetch("SELECT * FROM shop WHERE guild=%s", (guild, ), db)
        storeitems = []
        for x in store:
            storeitems.append({"name": x["name"], "channel": x["channel"], "role": x["role"], "type": str(x["type"]), "price": x["price"]})

        return jsonify({"enabled": levelsres[0]["levels"], "channels": channelres, "shop": storeitems})


    @levels_c.route("/api/updateLevels", methods=["POST"])
    async def updateLevels():
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

        if "channels" in props:

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

        if "shop" in props:
            shop = list(props["shop"])

            if len(shop) > 6:
                return "", 400 

            dc = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
            dc.execute("DELETE FROM shop WHERE guild = %s", (guild,))

            for ch in shop:

                try: 
                    name = str(ch["name"])
                    price = int(ch["price"])
                    tipo = int(ch["type"])
                    role = str(ch["role"])
                    channel = str(ch["channel"]) 

                except:
                    db.rollback()
                    dc.close()
                    return "", 400

                try:
                    dc.execute('''INSERT INTO 
                    shop(guild, name, price, type, role, channel)
                    VALUES(%s,%s,%s,%s,%s,%s)
                    ''', (guild, name, price, tipo, role, channel))
                except:
                    print(f"{guild}, {name}, {price}, {tipo}, {role}, {channel}")
                    db.rollback()
                    dc.close()
                    return "", 400

            db.commit()
            dc.close()

        return "", 200


    return levels_c