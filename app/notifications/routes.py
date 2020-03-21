# app/notifications/routes.py
from flask import render_template, flash, jsonify, request, redirect, url_for, session, current_app
from app.notifications import notifications
from app.notifications.models import Notification
from app.auth.models import User
from app.blocks.models import Block
from app.likes.models import Like
from app.visitors.models import Visitor
from app import db, limiter
from datetime import datetime
from werkzeug.wrappers import Response

#Needs to check if the method is POST and handle differently by pulling the POST variables
@notifications.route('/notifications', methods=['GET', 'POST'])
def show_notifications():
	n = db.session.query(Notification, User) \
			.join(User, Notification.sent_by_id==User.id) \
			.filter(Notification.owner_id == session['user_id']) \
			.order_by(Notification.time_sent.desc()) \
			.limit(100) \
			.all()
	return render_template('notifications.html', notifications=n, chat_notif=True)

@notifications.route('/read_message', methods=['POST'])
def read_message():
	try:
		notification = Notification.query.filter_by(owner_id = session['user_id'], sent_by_id = request.json['sender'], event_id = 5).first()
		if not notification:
			pass
		else:
			notification.remove_notification()
		notification = Notification.query.filter_by(owner_id = session['user_id'], sent_by_id = request.json['sender'], event_id = 3).first()
		if not notification:
			pass
		else:
			notification.remove_notification()
		return "Status OK"
	except:
		return "error"

@notifications.route('/get_update', methods=['POST'])
@limiter.exempt
def get_update():
	try:
		if request.host == current_app.config['ROOT_URL']:
			n = db.session.query(Notification.id, \
								Notification.owner_id, \
								Notification.sent_by_id, \
								Notification.event_id, \
								Notification.time_sent, \
								) \
					.filter(Notification.owner_id == session['user_id']) \
					.order_by(Notification.time_sent.desc()) \
					.all()
			return jsonify(notifications=n)
		return "error"
	except:
		return "error"

@notifications.route('/mark_read', methods=['POST'])
def mark_read():
	try:
		n = Notification.query.get(request.json['notification_id'])
		if n and n.owner_id == int(session['user_id']):
			n.remove_notification()
			return "Status OK"
		return "error"
	except:
		return "error"

@notifications.route('/mark_all_read', methods=['POST'])
def mark_all_read():
	n = Notification.query.filter_by(owner_id = session['user_id']).all()
	if n:
		[x.remove_notification() for x in n]
	return "Status OK"
	
@notifications.errorhandler(429)
def ratelimit_handler(error):
	return render_template('429.html'), 429