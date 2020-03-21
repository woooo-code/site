# app/likes/routes.py
from app.likes import likes
from app.auth.models import User
from app.likes.models import Like
from app.main.models import Picture
from app.notifications.models import Notification
from app import db
from flask import render_template, flash, jsonify, request, redirect, url_for, session
from datetime import datetime
from werkzeug.wrappers import Response

@likes.route('/like', methods=['POST'])
def like_user():
	try:
		if request.json['liked_id'].isdigit() is False:
			return "error"
		liked_id = int(request.json['liked_id'])
		exists = Like.query.filter_by(liked_id=liked_id, liked_by_id= session['user_id']).first()
		timestamp = datetime.now()

		if not exists: #Like
			like = Like.like_user(liked_id=liked_id, liked_by_id= session['user_id'])
			mutual_like = Like.query.filter_by(liked_id = session['user_id'], liked_by_id = liked_id).first()
			if mutual_like:
				notification = Notification.query.filter_by(owner_id = liked_id, sent_by_id = session['user_id'], event_id = 3).first()
				if not notification:
					Notification.create_notification(liked_id, session['user_id'], 3, timestamp)
					mutual = Notification.query.filter_by(owner_id = session['user_id'], sent_by_id = liked_id, event_id = 3).first()
					if not mutual:
						Notification.create_notification(session['user_id'], liked_id, 3, timestamp)
					else:
						mutual.update_notification()
					opposite = Notification.query.filter_by(owner_id = liked_id, sent_by_id = session['user_id'], event_id = 4).first()				
					if opposite:
						opposite.remove_notification()
				else:
					notification.update_notification()
					mutual = Notification.query.filter_by(owner_id = session['user_id'], sent_by_id = liked_id, event_id = 3).first()
					if not mutual:
						Notification.create_notification(session['user_id'], liked_id, 3, timestamp)
					else:
						mutual.update_notification()
					opposite = Notification.query.filter_by(owner_id = liked_id, sent_by_id = session['user_id'], event_id = 4).first()				
					if opposite:
						opposite.remove_notification()
			else:
				notification = Notification.query.filter_by(owner_id = liked_id, sent_by_id = session['user_id'], event_id = 2).first()
				if not notification:
					Notification.create_notification(liked_id, session['user_id'], 2, timestamp)
					opposite = Notification.query.filter_by(owner_id = liked_id, sent_by_id = session['user_id'], event_id = 4).first()				
					if opposite:
						opposite.remove_notification()
				else:
					notification.update_notification()
			if mutual_like:
				return jsonify(like_result="Unlike",chat=True)
			return jsonify(like_result="Unlike",chat=False)
		else: #Unlike
			notification = Notification.query.filter_by(owner_id = liked_id, sent_by_id = session['user_id'], event_id = 4).first() #Someone unliked
			if not notification:
				Notification.create_notification(liked_id, session['user_id'], 4, timestamp)
				opposite = Notification.query.filter_by(owner_id = liked_id, sent_by_id = session['user_id'], event_id = 2).first()
				if opposite:
					opposite.remove_notification()
				opposite = Notification.query.filter_by(owner_id = liked_id, sent_by_id = session['user_id'], event_id = 3).first()
				if opposite:
					opposite.remove_notification()
					opposite = Notification.query.filter_by(owner_id = session['user_id'], sent_by_id = liked_id, event_id = 3).first()
					opposite.remove_notification()
			else:
				notification.update_notification()
				opposite = Notification.query.filter_by(owner_id = liked_id, sent_by_id = session['user_id'], event_id = 2).first()
				if opposite:
					opposite.remove_notification()
				opposite = Notification.query.filter_by(owner_id = liked_id, sent_by_id = session['user_id'], event_id = 3).first()
				if opposite:
					opposite.remove_notification()
					opposite = Notification.query.filter_by(owner_id = session['user_id'], sent_by_id = liked_id, event_id = 3).first()
					opposite.remove_notification()
			exists.remove_like()
			return jsonify(like_result="Like",chat=False)
	except:
		return "error"

@likes.route('/liked_users')
def like_page():
	user = User.query.get(session['user_id'])
	if not user.validate_user():
		return redirect(url_for('authentication.set_up_profile'))
	liked_users = db.session.query(User, Like, Picture) \
					.join(Like, \
						User.id == Like.liked_id) \
					.filter(Like.liked_by_id == user.id) \
					.outerjoin(Picture, \
						User.id == Picture.uid) \
					.filter((Picture.profile_picture == True) | (Picture.profile_picture == None)) \
					.all()
	return render_template('whitelist.html', whitelist=liked_users)

@likes.errorhandler(429)
def ratelimit_handler(error):
	return render_template('429.html'), 429