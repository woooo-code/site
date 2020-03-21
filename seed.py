from faker import Faker
from app import create_app, db
from app.auth.models import User
from app.main.models import Picture
from app.tags.models import Tag
from datetime import datetime
import os, json

# execute get_cities_lat_lng.py to get positions.json file
with open('positions.json') as f:
    loc_data = json.load(f)

# execute get_profile_images.py to save images, upload to amazon s3 and get url
with open ('profile_images.txt') as f2:
	url_data = f2.read().splitlines()

with open ('interests.txt') as f3:
	tag_data = f3.read().splitlines()

seed_data = Faker()

if __name__ == '__main__':
	flask_app = create_app('dev')
	with flask_app.app_context():
		db.create_all()

		for _ in range (500):
			if seed_data.boolean(chance_of_getting_true=50):
				gender = 'male'
			else:
				gender = 'female'
			random_int = seed_data.random_int(min=0, max=2)
			if random_int == 0:
				preference = 'female'
			elif random_int == 1:
				preference = 'male'
			else:
				preference = 'both'

			# skip duplicate username and email
			exists = True
			while exists: 
				email = seed_data.last_name()
				username = seed_data.user_name()
				exists = User.query.filter((User.username==username) | (User.email==email)).first()

			random_int = seed_data.random_int(min=0, max=(len(loc_data) - 1))
			position = loc_data[random_int]['position'].split(',')[0]
			lat = loc_data[random_int]['lat']
			lng = loc_data[random_int]['lng']

			random_int = seed_data.random_int(min=0, max=(len(url_data) - 1))
			url = url_data[random_int]

			# add login time to some users so they appear online
			if seed_data.boolean(chance_of_getting_true=50):
				login_time = datetime.now()
			else:
				login_time = None

			user = User.create_user(first=seed_data.first_name(),
							last=seed_data.last_name(),
							email=email,
							activation=None,
							username=username,
							password='asdfasdf1',
							gender=gender,
							age=seed_data.random_int(min=18, max=40),
							preference=preference,
							position=position,
							lat=lat,
							lng=lng,
							biography=seed_data.text(max_nb_chars=200),
							login_time=login_time
							)


			Picture.add_pic(uid=user.id,
							url=url,
							profile_picture=True)

			random_int = seed_data.random_int(min=0, max=(len(tag_data) - 1))
			tag = tag_data[random_int]

			Tag.add_tag(tag_uid=user.id,
						tag=tag)

		# add admin account
		User.create_user(first="admin",
					last="admin",
					email="admin@matcha.com",
					activation=None,
					username="admin",
					password="asdfasdf1",
					gender="male",
					age=21,
					preference="both",
					position="Pluto",
					lat=0,
					lng=0,
					biography="I love you so Matcha :)",
					login_time=datetime.now(),
					admin=True	
					)
			
		os._exit(-1)
