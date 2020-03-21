# app/blocks/routes.py
from app.blocks import blocks
from app.main.models import Picture
from app.blocks.models import Block
from app.auth.models import User
from app import db
from flask import render_template, flash, request, redirect, url_for, session
from werkzeug.wrappers import Response

@blocks.route('/blocks', methods=['POST'])
def block_user():
	try:
		blocked_id = request.json['block_id']
		blocked_by_id = session['user_id']
		exists = Block.query.filter_by(blocked_id=blocked_id,blocked_by_id=blocked_by_id).first()
		if not exists:
			block = Block.create_block(blocked_id, blocked_by_id)
			return "Unblock"
		else:
			exists.remove_block()
			return "Block"
	except:
		return "error"

@blocks.route('/blocked_users')
def block_page():
	user = User.query.get(session['user_id'])
	# if not user.validate_user():
	# 	return redirect(url_for('authentication.set_up_profile'))
	blocked_users = db.session.query(User, Picture) \
					.join(Block, \
						User.id == Block.blocked_id) \
					.filter(Block.blocked_by_id == user.id) \
					.outerjoin(Picture, \
						User.id == Picture.uid) \
					.all()
	return render_template('blacklist.html', blacklist=blocked_users)

@blocks.errorhandler(429)
def ratelimit_handler(error):
	return render_template('429.html'), 429