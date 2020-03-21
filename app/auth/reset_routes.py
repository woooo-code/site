# app/auth/reset_routes.py
from flask import render_template, request, flash, redirect, url_for, session, current_app, json
from flask_mail import Message
from app.auth.forms import ForgotPasswordForm, HashResetForm
from app.auth import authentication
from app.auth.models import User
from app import db, mail, bcrypt

@authentication.route('/forgot', methods=['GET', 'POST'])
def forgot():
	if request.args.get('expired') and int(request.args.get('expired')) == 1:
		flash("This reset link has expired. Please request another password reset.")

	token = request.args.get('token', None)
	form = ForgotPasswordForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user:
			token = user.get_token()
			user.forgot_pwd = token
			link = url_for('authentication.reset', pass_hash=user.forgot_pwd, _external=True)
			msg = Message("Password Reset Link",
						sender=("Matcha", "matcha.dating.app@gmail.com"),
						recipients=[user.email])

			msg.html = "Hello " + user.first_name + ",<br /> <br />You have requested a password " \
			 			+ "reset link.<br /><br />Below is a link to reset your password that expires " \
			 			+ " in 24 hours<br /><br /><a href=\""+ link \
			 			+ "\">Click here to reset your password</a>"
			mail.send(msg)
			db.session.add(user)
			db.session.commit()
		flash('Please check your email for the reset link')
	return render_template('forgot.html', form=form)

@authentication.route('/reset/<pass_hash>', methods=['GET', 'POST'])
def reset(pass_hash):
	try:
		user = User.query.filter_by(forgot_pwd=pass_hash).first()
		form = HashResetForm()
		if pass_hash and user and user.verify_token(pass_hash):
			if form.validate_on_submit():
				if not user.verify_token(pass_hash):
					msg="This reset link has expired. Please request another password reset."
					return redirect(url_for('authentication.forgot', expired=1))
				user.password = bcrypt.generate_password_hash(form.newpassword.data).decode('utf-8')
				user.forgot_pwd = None
				db.session.add(user)
				db.session.commit()
				flash("Your password has been changed!")
				return redirect(url_for('authentication.sign_in_user'))
		else:
			msg="This reset link has expired. Please request another password reset."
			user.forgot_pwd = None
			db.session.add(user)
			db.session.commit()
			return redirect(url_for('authentication.forgot', expired=1))
	except:
		return render_template('404.html'), 404
	return render_template('reset.html', form=form)