# app/home/__init__.py
from flask import Blueprint, request, session, redirect, url_for
main = Blueprint('main', __name__, template_folder='templates')
from app.main import routes
from app.auth.models import User

@main.before_request
def before_request():
	if not session.get('_id'):
		if request.method == 'POST':
			return "error"
		elif request.path == '/home':
			return redirect(url_for('authentication.sign_in_user'))
		else:
			return redirect(url_for('main.home'))

	if session.get('user_id'):
		user = User.query.get(session['user_id'])
		if request.method == 'GET':
			session['notif_count'] = str(user.update_count())
		if not user.validate_user():
			return redirect(url_for('authentication.set_up_profile'))
		elif '/sign_s3' in request.path or '/save_pic' == request.path:
			return None
		# elif session.get('profile_pic') is not None \
		# 	and session['profile_pic'] is False \
		# 	and ('/profile/' + session['user_id']) not in request.path:
		# 	return redirect(url_for('main.view_user_profile', user_id=session['user_id']))