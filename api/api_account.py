from quart import Blueprint, redirect, jsonify, request, url_for
from quart_discord import requires_authorization, Unauthorized
import os 
import psycopg2.extras

from commons import db_fetch

def account_bp(discord, db):
    '''
    '''

    api_account = Blueprint("api_account", __name__)

    @api_account.route('/api/updateAccount', methods=["POST"])
    async def updateAccount():
        uid = "0"
        if os.environ.get('DISABLE_AUTH') == 'True':
            uid = "254672103465418752"
        else:
            Value = await discord.authorized
            if not Value:
                return "", 401
            user = await discord.fetch_user()
            uid = str(user.id)

        data = await request.get_json()
        try: 
            props = data["data"]
        except: 
            return "", 400

        try:
            month = int(props["month"])
            day = int(props["day"])
            enabled = int(props["enabled"])
        except:
            return "", 400

        dc = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

        dc.execute("SELECT * FROM users WHERE id = %s", (uid, ))
        data = dc.fetchall()

        if enabled:
            if not data:
                dc.execute("INSERT INTO users(id, month, day) VALUES(%s,%s,%s)", (uid, month, day,))
                db.commit()

            else:
                dc.execute("UPDATE users SET month = %s, day = %s WHERE id = %s", (month, day, uid, ))
                db.commit()

        else: 
            if data:
                dc.execute("DELETE FROM users WHERE id = %s", (uid, ))
                db.commit()

        dc.close()
        return ""

    @api_account.route('/api/account')
    async def account():
        uid = "0"

        if os.environ.get('DISABLE_AUTH') == 'True':
            uid = "254672103465418752"
            avatar = "https://cdn.discordapp.com/avatars/254672103465418752/774a470ec9ebde469d5c47c321b6a5e7.png"
            name = "kv"
        else:
            Value = await discord.authorized
            if not Value:
                return "", 401
            user = await discord.fetch_user()
            uid = str(user.id)
            avatar = user.avatar_url
            name = str(user)

        data = db_fetch("SELECT * FROM users WHERE id = %s", (uid, ), db)

        if data:
            data = data[0]
            return jsonify({
                "enabled": 1, 
                "day": data["day"], 
                "month" : data["month"],
                "avatar": avatar,
                "name": name})
        else:
            return jsonify({
                "enabled": 0, 
                "day": 1, 
                "month" : 1,
                "avatar": avatar,
                "name": name})

    return api_account