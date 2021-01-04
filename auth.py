import os 

async def has_access(discord, guild, dc):
  if os.environ.get('DISABLE_AUTH') == 'True':
    return True
  else: 

    Value = await discord.authorized
    if not Value: 
      return False  

    user = await discord.fetch_user()
    uid = user.id

    datad = await dc.execute("SELECT * FROM access WHERE id = ? AND guild = ?", (uid, guild,))
    data = await datad.fetchall()

    if not data:
      return False

    return True