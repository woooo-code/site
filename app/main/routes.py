# app/main/routes.py
from app.main import main
from app import db, bcrypt#, limiter
from app.auth.models import User
from app.blocks.models import Block
from app.likes.models import Like
from app.main.models import Picture
from app.tags.models import Tag
from app.notifications.models import Notification
from app.main.forms import UploadImageForm
from app.visitors.routes import visited
from flask import render_template, flash, request, redirect, url_for, session, jsonify
from werkzeug.utils import secure_filename
import os, json, boto3
from math import radians, cos, sin, asin, sqrt, pi, atan2, e, pow
from sqlalchemy.orm import load_only
from sqlalchemy.sql import func
from werkzeug.wrappers import Response

def get_dist(lat1, lng1, lat2, lng2):
	# use haversine formula to get distance between two lat and lng values
	# mean radius of earth in km
	# function returns distance in km
	radius = 6371
	delta_lat, delta_lng = (lat2 - lat1) * pi / 180, (lng2 - lng1) * pi / 180

	lat1, lat2 = lat1 * pi / 180, lat2 * pi / 180

	a = sin(delta_lat / 2) * sin(delta_lat / 2) + sin(delta_lng / 2) * sin(delta_lng / 2) * cos(lat1) * cos(lat2)
	c = 2 * atan2(sqrt(a), sqrt(1 - a))
	return round(radius * c)

def match_query(user, lat, lng):
	x = db.session.query(User, Block, Picture) \
				.outerjoin(Block, \
					((User.id == Block.blocked_id) & \
						(user.id == Block.blocked_by_id)) | \
					((User.id == Block.blocked_by_id) & \
						(user.id == Block.blocked_id))) \
				.filter(Block.blocked_id == None, \
					User.id != session['user_id'], \
					((User.lat != None) & (User.lng != None)), \
					((User.lat < lat + 4.0) & (User.lat > lat - 4.0) & \
						(User.lng < lng + 4.0) & (User.lng > lng - 4.0)), \
					(((User.gender == 'male') | (User.gender == 'female')) \
						if user.preference == 'both' \
						else (User.gender == user.preference)), \
					((User.preference == user.gender) | (User.preference == 'both'))) \
				.outerjoin(Picture, \
					User.id == Picture.uid) \
				.filter(Picture.profile_picture == True) \
				.limit(100)
	return x.all()

@main.route('/home')
def home():
	user = User.query.get(session['user_id'])
	if not user.validate_user():
		return redirect(url_for('authentication.set_up_profile'))
	
	if not user.lat or not user.lng:
		lat, lng = float(user.true_lat), float(user.true_lng)
	else:
		lat, lng = float(user.lat), float(user.lng)

	matches = match_query(user, lat, lng)
	match_results = []	

	session['dist'] = {}
	session['tags_match'] = {}
	session['rating'] = {}

	for match in matches:
			# calculate user rating based on distance and number of matching tags
			session['dist'][match.User.id] = get_dist(lat, lng, float(match.User.lat), float(match.User.lng))
			matching_tags = db.session.query(Tag.tag).group_by(Tag.tag).filter((Tag.tag_uid==match.User.id) | (Tag.tag_uid==session['user_id'])).having((func.count(Tag.tag) == 2 )).count()
			session['tags_match'][match.User.id] = matching_tags
			session['rating'][match.User.id] = int(round((100 * pow(e, -0.15 * (session['dist'][match.User.id]) / 25 )) + (e * session['tags_match'][match.User.id]), 0))
			
			like_action = Like.get_like_action(match.User.id, session['user_id'])
			user_tags = db.session.query(Tag.tag).filter(Tag.tag_uid == match.User.id).all()
			tags = ''.join(str(x[0]) + ',' for x in user_tags)[:-1]

			match_results.append({ 'uid' : match.User.id,
									'username' : match.User.username,
									'age' : match.User.age,
									'position' : match.User.position,
									'rating' : session['rating'][match.User.id],
									'profile_pic_url' : match.Picture.url if match.Picture else False,
									'like_action' : like_action,
									'tags' : tags})

	match_results.sort(key=lambda x: x['rating'], reverse=True)			
	return render_template('home.html', match_results=match_results[:49])

@main.route('/profile/<user_id>', defaults={'preview' : None}, methods=['GET', 'POST'])
@main.route('/profile/<user_id>/<preview>', methods=['GET', 'POST'])
# @limiter.limit('3 per day')
def view_user_profile(user_id, preview=None):
	if user_id.isdigit() is False:
		return redirect(url_for('main.home'))
	block = Block.query.filter((Block.blocked_id == session['user_id']) & (Block.blocked_by_id == user_id)).first()
	if block:
		return redirect(url_for('main.home'))

	# preview is only set to error if an error occurs when trying to upload a profile image
	if preview == "error":
		flash("An error occured, please try again")
		return redirect(url_for('main.view_user_profile', user_id=session['user_id']))

	block_button = "Block"
	matched = False
	offline = False
	user = User.query.get(session['user_id'])
	# if viewing another user's profile, check if user_id exists
	if user_id != session['user_id']:
		user = User.query.get(user_id)
		block = Block.query.filter_by(blocked_id=user_id, blocked_by_id=session['user_id']).first()
		if Like.query.filter_by(liked_id = user_id, liked_by_id = session['user_id']).first() and Like.query.filter_by(liked_id = session['user_id'], liked_by_id = user_id).first():
			matched = True
		# redirect if user id does not exist
		if not user:
			return redirect(url_for('main.home'))
		if block:
			block_button = "Unblock"
		# check if user is online
		if not user.login_time or (user.login_time and user.logout_time and user.logout_time >= user.login_time):
			offline = user.logout_time.strftime('%Y-%m-%d %I:%m %p')

	visited(user_id)

	profile_pic = Picture.query.filter_by(uid=user_id, profile_picture=True).first()
	other_pics = Picture.query.filter_by(uid=user_id, profile_picture=False).all()

	tags = Tag.query.filter_by(tag_uid=user_id).all()

	like_action = Like.get_like_action(user_id, session['user_id'])
	return render_template('user_profile.html', 
							user=user, 
							current_user_id=int(session['user_id']), 
							profile_pic=profile_pic,
							other_pics=other_pics,
							tags=tags,
							offline=offline,
							block_button=block_button,
							like_action=like_action,
							matched=matched, 
							preview=preview)

@main.route('/sign_s3')
def sign_s3():
	S3_BUCKET = os.environ.get('S3_BUCKET')
	file_name = str(session['user_id']) + "-" + request.args.get('file_name')
	file_type = request.args.get('file_type')
	file_size = request.args.get('file_size')

	# check for valid file types
	if file_type != "image/png" and file_type != "image/jpg" and file_type != "image/jpeg":
		flash("Images only!")
		return "error"

	# check for file size
	if int(file_size) > 250000:
		flash("File too large")
		return "error"

	s3 = boto3.client('s3')
	presigned_post = s3.generate_presigned_post(
		Bucket = S3_BUCKET,
		Key = file_name,
		Fields = {"acl": "public-read", "Content-Type": file_type},
		Conditions = [
		  {"acl": "public-read"},
		  {"Content-Type": file_type}
		],
		ExpiresIn = 3600
	)

	return json.dumps({
		'data': presigned_post,
		'url': 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, file_name)
	})

@main.route('/save_pic', methods=['POST'])
def save_profile_pic():
	try:
		print(request.json)
		url = request.json['url'] # Audit when ORM is deprecated
		picture = Picture.add_pic(
			uid=session['user_id'],
			url=url)

		session['num_pic'] += 1
		# set profile_picture to true if it's the only picture
		if session['num_pic'] == 1:
			Picture.set_profile_pic(session['user_id'], picture.id)
			session['profile_pic'] = True
		return "OK"
	except:
		flash("An error occured, please try again")
		return "error"

@main.route('/set_profile_pic', methods=['POST'])
def change_profile_pic():
	try:
		if request.json['pic_id'].isdigit() is False:
			return "error"
		pic_id = int(request.json['pic_id'])
		Picture.set_profile_pic(session['user_id'], pic_id)
		session['profile_pic'] = True
		return "OK"
	except:
		return "error"

@main.route('/delete_pic', methods=['POST'])
def delete_pic():
	try:
		if request.json['pic_id'].isdigit() is False:
			return "error"
		pic_id = int(request.json['pic_id'])
		picture = Picture.query.get(pic_id)
		picture.remove_pic()
		session['num_pic'] -= 1
		if request.json['is_profile_pic']:
			session['profile_pic'] = False
		return "OK"
	except:
		return "error"

@main.errorhandler(429)
def ratelimit_handler(error):
	return render_template('429.html'), 429