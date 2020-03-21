# app/auth/__init__.py
from flask import Blueprint, request, current_app, session, redirect, url_for
notifications = Blueprint('notifications', __name__, template_folder='templates')
from app.notifications import routes
from app.auth.models import User

@notifications.before_request
def before_request():
	if not session.get('_id'):
		if request.method == 'POST':
			return "error"
		else:
			return redirect(url_for('main.home'))

	if session.get('user_id'):
		if request.path == '/get_update':
			refer_path = request.referrer[len(request.url_root)-1:]
			no_login = ['/activate', '/forgot', '/register', '/reset', '/setup']
			
			if request.path == '/':
				return "error"
			for url in no_login:
				if request.path.find(url) == 0:
					return "error"
			return None

		user = User.query.get(session['user_id'])
		if request.method == 'GET':
			session['notif_count'] = str(user.update_count())
		if not user.validate_user():
			return redirect(url_for('authentication.set_up_profile'))