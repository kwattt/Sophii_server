from quart import Blueprint, redirect, jsonify, request, url_for
from quart_discord import requires_authorization, Unauthorized
import os 

def account_bp(discord, db, dc):
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
      uid = user.id

    data = await request.get_json()
    try: 
      props = data["data"]
    except: 
      return "", 400

    try:
      month = props["month"]
      day = props["day"]
      enabled = props["enabled"]
    except:
      return "", 400

    datad = await dc.execute("SELECT * FROM users WHERE id = ?", (uid, ))
    data = await datad.fetchall()

    if enabled:
      if not data:
        await dc.execute("INSERT INTO users(id, month, day) VALUES(?,?,?)", (uid, month, day,))
        await db.commit()

      else:
        await dc.execute("UPDATE users SET month = ?, day = ? WHERE id = ?", (month, day, uid, ))
        await db.commit()

    else: 
      if data:
        await dc.execute("DELETE FROM users WHERE id = ?", (uid, ))
        await db.commit()
      else: 
        return ""

    return ""

  @api_account.route('/api/account')
  async def account():
    uid = "0"
    if os.environ.get('DISABLE_AUTH') == 'True':
      uid = "254672103465418752"
    else:
      Value = await discord.authorized
      if not Value:
        return "", 401

      user = await discord.fetch_user()
      uid = user.id

    datad = await dc.execute("SELECT * FROM users WHERE id = ?", (uid, ))
    data = await datad.fetchall()

    if data:
      data = data[0]
      return jsonify({
        "enabled": 1, 
        "day": data["day"], 
        "month" : data["month"]})
    else:
      return jsonify({
        "enabled": 0, 
        "day": 1, 
        "month" : 1})

  return api_account