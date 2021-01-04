from quart import Blueprint, redirect, jsonify, request, url_for
from quart_discord import requires_authorization, Unauthorized
import os 

def api_bp(discord):
  '''
    Esta función contiene los endpoints de login, autorización y revoke.

    :param discord: 
      Instancia de quart_discord.
  '''
  api_control = Blueprint("api_control", __name__)

  @api_control.route('/api/login')
  async def login():
    '''
      Redirigir a discord para su autentificación
    '''
    return await discord.create_session()

  @api_control.route('/api/authorized')
  async def isAuthorized():
    '''
      Comprobar si el usuario está autorizado.
      :return Value:
        Booleano con la autorización
    '''

    Value = False

    if os.environ.get('DISABLE_AUTH') == 'True':
      Value = True
    else:
      Value = await discord.authorized

    return jsonify({"Auth": Value})

  @api_control.route('/api/revoke/')
  async def revoked():
    discord.revoke()
    return redirect("/")

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