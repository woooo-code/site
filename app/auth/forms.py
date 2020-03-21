# app/auth/forms.py
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, PasswordField, BooleanField, IntegerField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp
from app.auth.models import User
import re

def valid_name(form, field):
	if len(field.data) > 20 or (len(field.data) > 0 and not re.match(r'^[a-zA-Z ]+$', field.data)):
		raise ValidationError('Name must contain letters only (20 max)')

def valid_email(form, field):
	match_format = re.match("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", field.data)
	if len(field.data) > 60 or (len(field.data) > 0 and not match_format):
		raise ValidationError('Invalid email')

def email_exists(form, field):
	email = User.query.filter_by(email=field.data).first()
	if email:
		raise ValidationError('Email already exist')

def username_exists_valid(form, field):
	if field.data:
		username = User.query.filter_by(username=field.data).first()
		if username:
			raise ValidationError('Username already exist')
		else:
			valid = re.match('^[\w_]+$', field.data)
			if not valid:
				raise ValidationError('Must contain letters, numbers or "_"')
			elif len(field.data) < 3 or len(field.data) > 20:
					raise ValidationError('Must be between 3 - 20 characters')

def age_limit(form, field):
	age = field.data
	if age < 18 or age > 100:
		raise ValidationError('Invalid age')

def valid_password(form, field):
	password = field.data
	if password and ((len(password) < 5 or len(password) > 100) or not re.match(r'(?=.*\d)(?=.*[a-zA-Z])', password)):
		raise ValidationError('Must be at least 5 or more characters and contain at least one number')

class RegistrationForm(FlaskForm):
	first = StringField("First Name", validators=[DataRequired(), Length(max=20), Regexp(r'^[\w ]+$')])
	last = StringField("Last Name", validators=[DataRequired(), Length(max=20), Regexp(r'^[\w ]+$')])
	email = StringField('Email', validators=[DataRequired(), Email(), Length(max=60), email_exists])
	username = StringField('Username', validators=[DataRequired(), Length(3, 20), username_exists_valid])
	password = PasswordField('Password', validators=[DataRequired(), Length(5, 100), Regexp(r'(?=.*\d)(?=.*[a-zA-Z])', message='Must be at least 5 or more characters and contain at least one number'), EqualTo('confirm', message='Password must match')])
	confirm = PasswordField('Confirm Password', validators=[DataRequired()])
	recaptcha = RecaptchaField()
	submit = SubmitField('Register')

class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(3,20), Regexp(r'^[\w]+$')])
	password = PasswordField('Password', validators=[DataRequired()])
	submit = SubmitField('Login')

class SetUpProfileForm(FlaskForm):
	age = IntegerField('Age*', validators=[DataRequired(), age_limit])
	gender = SelectField('Gender*', choices=[('male', 'Male'), ('female','Female')], validators=[DataRequired()])
	preference = SelectField('Interested In*', choices=[('female', 'Female'), ('male','Male'), ('both', 'Both')], validators=[DataRequired()])
	pos = StringField("Location", validators=[Length(max=50), Regexp(r'^[\w ,.-]+$')])
	bio = TextAreaField("Biography", validators=[Length(max=1000)], render_kw={"placeholder": "1000 characters max"})
	submit = SubmitField('Save')

class ForgotPasswordForm(FlaskForm):
	email = StringField("Email", validators=[DataRequired(), Email(), Length(max=60)], render_kw={"placeholder": "Enter your email"})
	submit = SubmitField('Submit')

class HashResetForm(FlaskForm):
	newpassword = PasswordField('New Password', validators=[DataRequired(), Length(5, 100), EqualTo('confirm', message='password must match')])
	confirm = PasswordField('Confirm Password', validators=[DataRequired()])
	submit = SubmitField('Submit')

class UpdateSettingsForm(FlaskForm):	
	first = StringField("First Name", validators=[valid_name])
	last = StringField("Last Name", validators=[valid_name])
	email = StringField('Email', validators=[email_exists, valid_email])
	username = StringField('Username', validators=[username_exists_valid])
	old_password = PasswordField('Current Password', render_kw={"placeholder": "********"})
	new_password = PasswordField('New Password', validators=[valid_password, EqualTo('confirm', message='Password must match')])
	confirm = PasswordField('Confirm Password')
	submit = SubmitField('Save Changes')

