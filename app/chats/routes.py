# app/chats/routes.py
from app import db, socketio
from app.chats import chats
from app.chats.models import Chat
from app.auth.models import User
from app.likes.models import Like
from app.blocks.models import Block
from app.notifications.models import Notification
from flask import render_template, redirect, url_for, session, flash, request, jsonify
from flask_socketio import SocketIO, send, emit
from sqlalchemy.orm import aliased
from datetime import datetime
from werkzeug.wrappers import Response

users = {}

@socketio.on('register_user')
def register_user():
	users[session['user_id']] = request.sid

@socketio.on('private_message', namespace='/private')
def private_message(payload):
	message = payload['message']

	# verify recipient can receive message from sender by checking blocks and likes
	parent = aliased(Like, name="parent")
	child = aliased(Like, name="child")
	can_message = db.session.query(User.id) \
			.outerjoin(Block, \
					((session['user_id'] == Block.blocked_id) & \
						(payload['user_id'] == Block.blocked_by_id)) | \
					((session['user_id'] == Block.blocked_by_id) & \
					 	(payload['user_id'] == Block.blocked_id))) \
			.filter(Block.blocked_id == None, User.id == payload['user_id']) \
			.join(parent, ((session['user_id'] == parent.liked_id) & (payload['user_id'] == parent.liked_by_id))) \
			.filter(session['user_id'] == parent.liked_id) \
			.join(child, \
				(child.liked_id == parent.liked_by_id) & \
				(child.liked_by_id == parent.liked_id)) \
			.first()

	if can_message and can_message[0] == int(payload['user_id']):
		Chat.save_message(sent_by_id=session['user_id'],
							received_by_id=payload['user_id'],
							message=message, 
							message_time=payload['timestamp'])

		notification = Notification.query.filter_by(owner_id = payload['user_id'], sent_by_id = payload['sender'], event_id = 5).first()
		if not notification:
			Notification.create_notification(payload['user_id'], payload['sender'], 5, datetime.now())
		else:
			notification.update_notification()

		if users.get(payload['user_id']):
			recipient_session_id = users[payload['user_id']]
			emit('new_private_message', payload, room=recipient_session_id)	

@chats.route('/chats', methods=['GET'])
def display_chats():
	referral_id = request.args.get('referral_id', None)
	parent = aliased(Like, name="parent")
	child = aliased(Like, name="child")
	chat_users = db.session.query(User, Block, parent, child) \
			.join(parent, ((parent.liked_id == User.id) & (parent.liked_by_id == session['user_id']))) \
			.filter(parent.liked_by_id == session['user_id']) \
			.outerjoin(Block, ((Block.blocked_id == User.id) & (Block.blocked_by_id == session['user_id'])) | \
				((Block.blocked_by_id == User.id) & (Block.blocked_id == session['user_id']))) \
			.filter(Block.blocked_id == None) \
			.join(child, \
				(child.liked_id == parent.liked_by_id) & \
				(parent.liked_id == child.liked_by_id)) \
			.limit(20) \
			.all()
	return render_template('chats.html', chat_users=chat_users, referral_id=referral_id, chat_notif=True)

@chats.route('/history', methods=['POST'])
def get_chat_history():
	try:
		recipient_id = request.json['recipient_id']

		if type(recipient_id) != int and recipient_id.isdigit() is False:
			return "error"
		parent = aliased(Like, name="parent")
		child = aliased(Like, name="child")
		# Validate the recipient_id isn't blocked or blocking current_user and that both users liked each other
		messages = db.session.query(Chat.sent_by_id, Chat.message, Chat.message_time) \
				.join(parent, ((session['user_id'] == parent.liked_id) & (recipient_id == parent.liked_by_id))) \
				.filter(session['user_id'] == parent.liked_id) \
				.join(child, \
					(child.liked_id == parent.liked_by_id) & \
					(child.liked_by_id == parent.liked_id)) \
				.outerjoin(Block, \
							((session['user_id'] == Block.blocked_id) & \
								(recipient_id == Block.blocked_by_id)) | \
							((session['user_id'] == Block.blocked_by_id) & \
							 	(recipient_id == Block.blocked_id))) \
				.filter(Block.blocked_id == None, ((Chat.sent_by_id==recipient_id) & (Chat.received_by_id==session['user_id'])) |\
						((Chat.received_by_id==recipient_id) & (Chat.sent_by_id==session['user_id']))) \
				.order_by(Chat.id.desc()) \
				.limit(100) \
				.all()
		# need to reverse messages on front end
		return jsonify(messages=messages)
	except:
		return "error"

@chats.errorhandler(429)
def ratelimit_handler(error):
	return render_template('429.html'), 429