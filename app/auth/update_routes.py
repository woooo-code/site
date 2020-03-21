# app/auth/update_routes.py
from flask import request, session, current_app, json
from app.auth import authentication
from app.auth.models import User, Report
from app import db, limiter
import requests
import re

def get_true_latlng(ip):
	# http://ip-api.com/docs/api:json
	str="http://ip-api.com/json/?callback=?{}".format(ip)
	result = requests.get(str).content.decode('utf-8')
	# remove ip address and ( appeneded to the beginning of response
	tmp = re.sub(r'.*{', '{', result)
	# remove ); from end of response and convert to json object
	result = json.loads(re.sub(r'\);$', '', tmp))
	return result['lat'], result['lon']

#position defaults to most specific location
def get_latlongpos(pos):
	# https://developers.google.com/maps/documentation/geolocation/intro
	if not pos:
		return None, None, None
	str="https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}" \
		.format(pos, current_app.config['GOOGLE_API_KEY'])
	result = json.loads(requests.get(str).content)
	if result['results']:
		return result['results'][0]['geometry']['location']['lat'], \
				result['results'][0]['geometry']['location']['lng'], \
				result['results'][0]['address_components'][0]['long_name']
	return None, None, pos

@authentication.route('/update_loc', methods=['POST'])
def update_location():
	try:
		new_loc = request.json['new_loc']
		user = User.query.get(session['user_id'])
		user.lat, user.lng, user.position = get_latlongpos(new_loc)
		db.session.add(user)
		db.session.commit()
		return user.position
	except:
		return "error"

@authentication.route('/update_age', methods=['POST'])
@limiter.exempt
def update_age():
	print("Fuuuuuck")
	try:
		print("Meow")
		new_age = request.json['new_age']
		if new_age.isdigit():
			user = User.query.get(session['user_id'])
			if int(new_age) >= 18 and int(new_age) <= 100:
				user.age = new_age
				db.session.add(user)
				db.session.commit()
				return new_age
		return "error"
	except:
		return "error"

@authentication.route('/update_gender', methods=['POST'])
def update_gender():
	try:
		new_gender = request.json['new_gender']
		user = User.query.get(session['user_id'])
		if new_gender == 'male' or new_gender == 'female':
			user.gender = new_gender
			db.session.add(user)
			db.session.commit()
			return new_gender
		return "error"
	except:
		return "error"

@authentication.route('/update_preference', methods=['POST'])
def update_preference():
	try:
		new_preference = request.json['new_preference']
		user = User.query.get(session['user_id'])
		if new_preference == 'male' or new_preference == 'female' or new_preference =='both':
			user.preference = new_preference
			db.session.add(user)
			db.session.commit()
			return new_preference
	except:
		return "error"

@authentication.route('/bio', methods=['POST'])
def edit_bio():
	try:
		bio = request.json['bio']
		user = User.query.get(session['user_id'])
		user.biography = bio
		db.session.add(user)
		db.session.commit()
		return "OK"
	except:
		return "error"
	
@authentication.route('/update_report', methods=['POST'])
def update_report():
	try:
		reported_user = request.json['reported_user']
		exists = Report.query.filter((Report.reported_user==reported_user) & (Report.reported_by==session['user_id'])).first()
		if not exists and reported_user != session['user_id']:
			Report.create_report(reported_user, session['user_id'])
		return "OK"
	except:
		return "error"
