import os 
import psycopg2.extras

async def has_access(discord, guild, db):
  if os.environ.get('DISABLE_AUTH') == 'True':
    return True
  else: 

    Value = await discord.authorized
    if not Value: 
      return False  

    user = await discord.fetch_user()
    uid = user.id
    
    dc = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    dc.execute("SELECT * FROM access WHERE id = %s AND guild = %s", (str(uid), str(guild),))
    data = dc.fetchone()
    dc.close()

    if not data:
      return False

    return True