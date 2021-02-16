from quart import Blueprint, redirect, jsonify, request, url_for
from quart_discord import requires_authorization, Unauthorized
import psycopg2.extras

from auth import has_access

from commons import db_commit, db_fetch

def extra_bp(discord, db):

    extra_c = Blueprint("extra_c", __name__)

    @extra_c.route("/api/updateExtra", methods=["POST"])
    async def updateExtra():

        data = await request.get_json()
        try: 
            guild = str(data['guild'])
            props = data["data"]
        except: 
            return "", 400

        if not (await has_access(discord, guild, db)):
            return "", 401

        if "bday" in props:

            try: 
                bday = str(props["bday"])
                bdaymsg = str(props["bdaymsg"])
                bdayutc = int(props["bdayutc"])
                bdaymsg.format(123)
            except:
                return "", 400

            if len(bdaymsg) > 350:
                return "", 400

            db_commit("UPDATE servidores SET birthday = %s, bdaymsg = %s, bdayutc = %s WHERE guild = %s", (bday, bdaymsg, bdayutc, guild, ), db)

        if "stalk" in props:

            try:
                stalk = int(props["stalk"])
                role = list(props["role"])
            except:
                return "", 400

            if len(role) > 20:
                return "", 400

            dc = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

            dc.execute("UPDATE servidores SET stalk = %s WHERE guild = %s", (stalk, guild, ))
            dc.execute("DELETE FROM stalkroles WHERE guild = %s", (guild,))

            for rol in role:
                dc.execute("INSERT INTO stalkroles(guild, role) VALUES(%s,%s)", (guild, rol,))

            db.commit()
            dc.close()

        if "msg" in props:
            
            try: 
                msgs = str(props["msg"])
            except:
                return "", 400

            if len(msgs) > 1000:
                return "", 400

            values = msgs.replace("\n", "").split(";")

            for msg in values:
                try:
                    msg.format(123)
                except (IndexError, KeyError, ValueError):
                    return "", 400

            dc = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
            dc.execute("DELETE from stalkmsg WHERE guild=%s", (guild,))

            for msg in values:
                if msg:
                    dc.execute("INSERT INTO stalkmsg(guild,msg) VALUES(%s,%s)", (guild,msg.lstrip(),))

            db.commit()
            dc.close()

        return "", 200

    @extra_c.route("/api/extra")
    async def Extra():

        try: 
            guild = request.args.get("guild")
        except:
            return "", 400

        if not (await has_access(discord, guild, db)):
            return "", 401

        data = db_fetch("SELECT stalk, bdaymsg, birthday, bdayutc FROM servidores WHERE guild=%s", (guild, ), db)

        if not data:
            return "", 400

        data = data[0]

        stalk = data["stalk"]
        bdaymsg = data["bdaymsg"]
        bday = str(data["birthday"])
        bdayutc = data["bdayutc"]

        messages = db_fetch("SELECT * FROM stalkmsg WHERE guild=%s", (guild, ), db)

        temp = []
        for x in messages:
            temp.append(x["msg"])
        temp = ";\n".join(temp)
        stalk_msg = temp 

        temp = []
        roles = db_fetch("SELECT * FROM stalkroles WHERE guild=%s", (guild, ), db)
        for x in roles:
            temp.append(str(x["role"]))
        stalk_roles = temp

        return jsonify({"role": stalk_roles, 
                        "msg": stalk_msg,
                        "bday": bday,
                        "stalk": stalk,
                        "bdaymsg": bdaymsg,
                        "bdayutc": bdayutc})

    return extra_c