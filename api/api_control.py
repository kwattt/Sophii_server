from quart import Blueprint, redirect, request
from api.handle_uri import handle_uri, process_oauth

api_control = Blueprint("api_control", __name__)
auth_url = handle_uri()

@api_control.route('/api/login')
async def login():
  '''
    Redirigir a discord para su autentificación
  '''
  return redirect(auth_url)

@api_control.route('/api/oauthds/')
async def redirect_oauth():
  '''
    Manejo del código otorgado por discord para la verificación de OAUTH2
  '''

  val = request.args.get("code")
  process_oauth(val)

  return "1"