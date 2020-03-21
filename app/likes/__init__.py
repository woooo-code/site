# app/likes/__init__.py
from flask import Blueprint, request, session, redirect, url_for
likes = Blueprint('likes', __name__, template_folder="templates")
from app.likes import routes
from app.auth.models import User

@likes.before_request
def is_logged_in():
	if not session.get('_id'):
		if request.method == 'POST':
			return "error"
		else:
			return redirect(url_for('main.home'))

	if session.get('user_id'):
		user = User.query.get(session['user_id'])
		if request.method == 'GET':
			session['notif_count'] = str(user.update_count())
		if not user.validate_user():
			return redirect(url_for('authentication.set_up_profile'))
		elif request.path == ('/profile/' + session['user_id']):
			return None
		# elif session.get('profile_pic') is not None and session['profile_pic'] is False:
		# 	return redirect(url_for('main.view_user_profile', user_id=session['user_id']))