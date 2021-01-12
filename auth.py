import os 

async def has_access(discord, guild, db):
  if os.environ.get('DISABLE_AUTH') == 'True':
    return True
  else: 

    Value = await discord.authorized
    if not Value: 
      return False  

    user = await discord.fetch_user()
    uid = user.id
    
    dc = db.cursor()
    dc.execute("SELECT * FROM access WHERE id = ? AND guild = ?", (uid, guild,))
    data = dc.fetchone()
    dc.close()

    if not data:
      return False

    return True