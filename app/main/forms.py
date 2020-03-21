# app/main/forms.py
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import SubmitField

class UploadImageForm(FlaskForm):
	file = FileField('Upload an Image')
	submit = SubmitField('Upload')

