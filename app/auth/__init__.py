# app/auth/__init__.py
from flask import Blueprint, request, current_app, session, redirect, url_for
authentication = Blueprint('authentication', __name__, template_folder='templates')
from app.auth import routes
from app.auth import reset_routes
from app.auth import settings_routes
# from app.auth import update_routes
from app.auth.models import User

@authentication.before_request
def before_request():
	if current_app.config['REDIRECT_HTTP'] is True:
		if not request.is_secure:
			return redirect(request.url.replace("http://", "https://"))

	no_login = ['/activate', '/forgot', '/register', '/reset']

	if not session.get('_id'):
		if request.method == 'POST' or request.method == 'GET':
			if request.path == '/':
				return None
			for url in no_login:
				if request.path.find(url) == 0:
					return None
		return redirect(url_for('authentication.sign_in_user'))

	if session.get('user_id'):
		if request.path == '/logout' or request.path == '/setup':
			return None
		user = User.query.get(session['user_id'])
		if request.method == 'GET':
			session['notif_count'] = str(user.update_count())
		if user.admin == False and request.path == '/admin':
			return redirect(url_for('main.home'))
		elif user.admin == True and request.path == '/admin':
			return None
		if not user.validate_user():
			return redirect(url_for('authentication.set_up_profile'))
		elif user.validate_user():
			if request.path == '/':
				return redirect(url_for('main.home'))
			for url in no_login:
				if request.path.find(url) == 0:
					return redirect(url_for('main.home'))