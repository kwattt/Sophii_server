from quart import Blueprint, redirect, jsonify, request, url_for

from quart_discord import requires_authorization, Unauthorized

def api_bp(discord):

  api_control = Blueprint("api_control", __name__)

  @api_control.route('/api/login')
  async def login():
    '''
      Redirigir a discord para su autentificación
    '''
    return await discord.create_session()

  @api_control.route('/api/authorized')
  async def isAuthorized():
    
    #Value = await discord.authorized
    Value = True

    return jsonify({"Auth": Value})

  @api_control.route('/api/oauthds/')
  async def redirect_oauth():
    '''
      -
    '''
    await discord.callback()
    return redirect("/panel")

  @api_control.errorhandler(Unauthorized)
  async def redirect_unauthorized(e):
      return redirect("/api/login")

  return api_control