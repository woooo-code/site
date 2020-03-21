# app/auth/settings_routes.py
from flask import render_template, redirect, flash, session, url_for
from app.auth import authentication
from app.auth.models import User
from app.auth.forms import UpdateSettingsForm
from app import db, bcrypt
from app.auth.routes import send_activation_email

@authentication.route('/settings', methods=['GET', 'POST'])
def update_settings():
	user = User.query.get(session['user_id'])
	form = UpdateSettingsForm()
	if form.validate_on_submit():
		username = form.username.data
		old_password = form.old_password.data
		new_password = form.new_password.data
		if new_password:
			if not old_password:
				flash("Please enter current password")
				return render_template('settings.html', form=form, user=user)
			elif user.check_password(old_password) is False:
				flash("Invalid credentials, please try again")
				return render_template('settings.html', form=form, user=user)
			else:
				user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
		if form.first.data:
			user.first_name = form.first.data
		if form.last.data:
			user.last_name = form.last.data
		if form.email.data:
			user.email = form.email.data
			user.activation = send_activation_email(form.email.data, user.first_name)
		if username:
			user.username = username
		db.session.add(user)
		db.session.commit()
		if user.activation:
			return redirect(url_for('authentication.log_out_user'))
		return redirect(url_for('authentication.update_settings'))
	return render_template('settings.html', form=form, user=user)
