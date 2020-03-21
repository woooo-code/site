# app/auth/routes.py
from flask import render_template, request, flash, redirect, url_for, session, current_app, json
from app.auth.forms import RegistrationForm, LoginForm, \
	SetUpProfileForm, ForgotPasswordForm, HashResetForm
from app.tags.forms import SkipSetUpTagsForm
from app.auth import authentication
from app.auth.models import User, Report
from app.auth.update_routes import get_true_latlng, get_latlongpos
from app.main.models import Picture
from app import db, mail, limiter
from flask_mail import Message
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer
import hashlib
import requests
import re
from sqlalchemy import func
from werkzeug.wrappers import Response

def send_activation_email(email, name):
	if current_app.config['ACCOUNT_ACTIVATION']:
		serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
		activation_token = serializer.dumps(email, salt=current_app.config['SECRET_KEY'])
		link = url_for('authentication.activate', activate_hash=activation_token, _external=True)
		msg = Message("Activate Your Account with Matcha",
			sender=("Matcha", "matcha.dating.app@gmail.com"),
			recipients=[email])

		msg.html = "Hello " + name + ",<br /> <br />Welcome to Matcha! " \
		 			+ "<br />Here is a link to activate your account: " \
		 			+ "<a href=\""+ link \
		 			+ "\">Click here to activate</a>"

		mail.send(msg)
		return activation_token
	return None

@authentication.route('/register', methods=['GET', 'POST'])
def register_user():
	form = RegistrationForm()
	if form.validate_on_submit():
		# generate token and send to user to activate account
		activation_token = send_activation_email(form.email.data, form.first.data)
				
		User.create_user(
			first=form.first.data,
			last=form.last.data,
			email=form.email.data,
			activation=activation_token,
			username=form.username.data,
			password=form.password.data)
		if current_app.config['ACCOUNT_ACTIVATION']:
			flash('Registration successful, check your email to activate account')
		else:
			flash('Registration successful')
		return redirect(url_for('authentication.sign_in_user'))		
	return render_template('registration.html', form=form, landing=True)

@authentication.route('/activate/<activate_hash>', methods=['GET', 'POST'])
def activate(activate_hash):
	try:
		if User.verify_activation_token(activate_hash):
			flash("Account activated, welcome to Matcha!")
		else:
			flash("Failed to activate account, try again")
	except:
		return render_template('404.html'), 404
	return redirect(url_for('authentication.sign_in_user'))

def _get_remote_addr():
    address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if address is not None:
        # An 'X-Forwarded-For' header includes a comma separated list of the
        # addresses, the first address being the actual remote address.
        address = address.encode('utf-8').split(b',')[0].strip()
    return address


def _create_identifier():
    user_agent = request.headers.get('User-Agent')
    if user_agent is not None:
        user_agent = user_agent.encode('utf-8')
    base = '{0}|{1}'.format(_get_remote_addr(), user_agent)
    if str is bytes:
        base = unicode(base, 'utf-8', errors='replace')  # pragma: no cover
    h = hashlib.sha512()
    h.update(base.encode('utf8'))
    return h.hexdigest()

@authentication.route('/', methods=['GET', 'POST'])
def sign_in_user():
	form = LoginForm()

	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if not user or user.check_password(form.password.data) is False:
			flash('Invalid credentials, please try again')
			return redirect(url_for('authentication.sign_in_user'))
		
		# check if user account is activated
		if user.activation != None:
			flash('Account not activated, please check your email')
			return redirect(url_for('authentication.sign_in_user'))
		# login user and save time of log in
		session['user_id'] = str(user.id)
		session['_id'] = _create_identifier()
		session['first_name'] = str(user.first_name)
		if user.admin == True:
			session['admin'] = True
		user.login_time = datetime.now()

		# query pictures table and save number of pictures in session variable
		pics = db.session.query(Picture.profile_picture).filter_by(uid=session['user_id']).all()
		session['num_pic'] = len(pics)
		session['profile_pic'] = False

		for pic in pics:
			if pic[0]:
				session['profile_pic'] = True
				break	
		# get user true lat and true lng to save to users table
		if not user.lat or not user.lng:
			ip = request.remote_addr
			user.true_lat, user.true_lng = get_true_latlng(ip)

		db.session.add(user)
		db.session.commit()

		# check if user profile is set up
		if session['profile_pic'] == False:
			if not 'rating' in session:
				session['rating'] = {}
			session['rating'][session['user_id']] = "N/A"
			return redirect(url_for('main.view_user_profile', user_id=session['user_id']))
		else:
			return redirect(url_for('main.home'))
			
	return render_template('login.html', form=form, landing=True)

@authentication.route('/admin', methods=['GET', 'POST'])
def admin_panel():
	reports = db.session.query(Report.reported_user, func.count(Report.reported_user), User.username) \
				.join(User, User.id == Report.reported_user) \
				.group_by(User.id, Report.reported_user) \
				.all()
	return render_template('admin.html', reports=reports)

@authentication.route('/setup', methods=['GET', 'POST'])
def set_up_profile():
	user = User.query.get(session['user_id'])
	form = SetUpProfileForm()
	if form.validate_on_submit():
		user.age = form.age.data
		user.gender = form.gender.data
		user.preference = form.preference.data
		user.lat, user.lng, user.position = get_latlongpos(form.pos.data)
		user.biography = form.bio.data
		db.session.add(user)
		db.session.commit()
		# save user preference as session variable
		session['preference'] = user.preference
		# flash('Profile set up successful')
		session['set_up_tags'] = True
		return redirect(url_for('authentication.set_up_tags'))
		# flash(request.remote_addr)
	return render_template('setup.html', form=form)

@authentication.route('/setup_tags', methods=['GET', 'POST'])
def set_up_tags():
	# only redirect user on first login
	session['set_up_tags'] = False
	form = SkipSetUpTagsForm()
	if form.validate_on_submit():
		return redirect(url_for('main.view_user_profile', user_id=session['user_id']))
	return render_template('setup_tags.html', form=form, setup=1)

@authentication.route('/logout', methods=['GET', 'POST'])
def log_out_user():
	# save time of log out, log out user and clear session variables
	user = User.query.get(session['user_id'])
	user.logout_time = datetime.now()
	db.session.add(user)
	db.session.commit()
	if session:
		session.clear()
	return redirect(url_for('authentication.sign_in_user'))

@authentication.app_errorhandler(404)
def page_not_found(error):
	return render_template('404.html'), 404

@authentication.errorhandler(429)
def ratelimit_handler(error):
	return render_template('429.html'), 429

@authentication.route('/429', methods=['GET'])
def too_many_requests():
	return render_template('429.html'), 429
