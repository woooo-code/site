# app/auth/models.py
from app import db, bcrypt
from flask import current_app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime

class User(UserMixin, db.Model):
	__tablename__ = "users"
	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String(20))
	last_name = db.Column(db.String(20))
	email = db.Column(db.String(60), unique=True)
	activation = db.Column(db.String(250))
	username = db.Column(db.String(20), unique=True)
	password = db.Column(db.String(100))
	forgot_pwd = db.Column(db.String(250))
	gender = db.Column(db.String(10))
	age = db.Column(db.Integer)
	preference = db.Column(db.String(20))
	position = db.Column(db.String(50))
	lat = db.Column(db.Numeric(precision=10, asdecimal=True))
	lng = db.Column(db.Numeric(precision=10, asdecimal=True))
	true_lat = db.Column(db.Numeric(precision=10, asdecimal=True))
	true_lng = db.Column(db.Numeric(precision=10, asdecimal=True))
	biography = db.Column(db.String(1000))
	login_time = db.Column(db.DateTime)
	logout_time = db.Column(db.DateTime, default=datetime.now())
	admin = db.Column(db.Boolean)


	def check_password(self, password):
		return bcrypt.check_password_hash(self.password, password)

	@classmethod
	def create_user(cls, first, last, email, activation, username, password, \
					gender=None, age=None, preference=None, position=None, \
					lat=None, lng=None, biography=None, login_time=None, logout_time=datetime.now(), admin=False):
		user = cls(first_name=first,
					last_name=last,
					email=email,
					activation=activation,
					username=username,
					password=bcrypt.generate_password_hash(password).decode('utf-8'),
					gender=gender,
					age=age,
					preference=preference,
					position=position,
					lat=lat,
					lng=lng,
					biography=biography,
					login_time=login_time,
					logout_time=logout_time,
					admin=admin
					)
		db.session.add(user)
		db.session.commit()
		return user

	def validate_user(self):
		if self.gender and self.age and self.preference:
			return True
		else:
			return None

	def get_token(self, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'user': self.id}).decode('utf-8')

	@staticmethod
	def verify_token(token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return None
		id = data.get('user')
		if id:
			return User.query.get(id)
		return None

	@staticmethod
	def verify_activation_token(token):
		serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
		try:
			data = serializer.loads(
						token,
						salt=current_app.config['SECRET_KEY'])
		except:
			return False
		user = User.query.filter_by(activation=token).first()
		if data and user and data == user.email:
			user.activation = None
			db.session.add(user)
			db.session.commit()
			return True
		return False

	def update_count(self):
		return Notification.query.filter(Notification.owner_id == self.id).count()

class Report(db.Model):
	__tablename__ = "reports"
	id = db.Column(db.Integer, primary_key=True)
	reported_user = db.Column(db.Integer, db.ForeignKey('users.id'))
	reported_by = db.Column(db.Integer, db.ForeignKey('users.id'))

	@classmethod
	def create_report(cls, reported_user, reported_by):
		user = cls(reported_user=reported_user, reported_by=reported_by)
		db.session.add(user)
		db.session.commit()
		return user

from app.notifications.models import Notification