from quart import Blueprint, redirect, jsonify, request, url_for
from quart_discord import requires_authorization, Unauthorized
import psycopg2.extras

from auth import has_access
from commons import db_fetch, db_commit

def msg_bp(discord, db):

    msg_c = Blueprint("msg_c", __name__)

    @msg_c.route("/api/updateMsg", methods=["POST"])
    async def updateMensajes():

        data = await request.get_json()
        try: 
            guild = str(data['guild'])
            props = data["data"]
        except: 
            return "", 400

        if not (await has_access(discord, guild, db)):
            return "", 401

        if "channel" in props:
            channel = str(props["channel"])
            if(len(channel) > 25):
                return "", 400

            db_commit("UPDATE servidores SET welcome = %s WHERE guild = %s", (channel, guild, ), db)

        if "join" in props:
            join = props["join"]
            ent = join.replace("\n", "").split(";")

            if len(join) > 1500:
                return "", 400

            for msg in ent:
                try:
                    msg.format(123)
                except (IndexError, KeyError, ValueError):
                    return "", 400
            
            dc = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
            dc.execute("DELETE from WELCOME WHERE guild=%s AND tipo=0", (guild,))
            
            for msg in ent:
                if msg:
                    dc.execute("INSERT INTO welcome(guild,tipo,msg) VALUES(%s,%s,%s)", (guild,0,msg.lstrip(),))
            
            db.commit()
            dc.close()

        if "leave" in props:
            leave = props["leave"]

            if len(leave) > 1500:
                return "", 400

            sal = leave.replace("\n", "").split(";")

            for msg in sal:
                try:
                    msg.format(123)
                except (IndexError, KeyError, ValueError):
                    return "", 400

            dc = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
            dc.execute("DELETE from WELCOME WHERE guild=%s AND tipo=1", (guild,))

            for msg in sal:
                if msg:
                    dc.execute("INSERT INTO welcome(guild,tipo,msg) VALUES(%s,%s,%s)", (guild,1,msg.lstrip(),))
            
            db.commit()
            dc.close()

        if "oraculo" in props:
            oraculo = props["oraculo"]

            if len(oraculo) > 1500:
                return "", 400

            oraculo = oraculo.replace("\n", "").split(";")

            for msg in oraculo:
                try:
                    msg.format(123)
                except (IndexError, KeyError, ValueError):
                    return "", 400

            dc = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
            dc.execute("DELETE from oraculo WHERE guild=%s", (guild,))

            for msg in oraculo:
                if msg:
                    dc.execute("INSERT INTO oraculo(guild,msg) VALUES(%s,%s)", (guild,msg.lstrip(),))
            
            db.commit() 
            dc.close()

        return "", 200

    @msg_c.route("/api/msg")
    async def Mensajes():
        try:
            guild = str(request.args.get("guild"))
        except:
            return "", 400

        if not (await has_access(discord, guild, db)):
            return "", 401

        dc = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        dc.execute("SELECT welcome FROM servidores WHERE guild=%s", (guild, ))
        data = dc.fetchall()

        welcome = str(data[0]["welcome"])

        dc.execute("SELECT * FROM oraculo WHERE guild=%s", (guild, ))
        extraD = dc.fetchall()
        
        temp = []
        for msg in extraD:
            if msg:
                temp.append(msg["msg"])
        oraculo = ";\n\n".join(temp)

        dc.execute("SELECT * FROM welcome WHERE guild=%s", (guild, ))
        welcomeres = dc.fetchall()

        ent = []
        sal = []
        for msg in welcomeres:
            if msg["tipo"] == 0:
                ent.append(msg["msg"])
            else:
                sal.append(msg["msg"])
        ent = ";\n\n".join(ent)
        sal = ";\n\n".join(sal)

        dc.close()

        return jsonify({"channel":welcome, 
                        "oraculo": oraculo, 
                        "join": ent, 
                        "leave": sal})

    return msg_c