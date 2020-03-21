# app/main/models.py
from app import db
from datetime import datetime

class Picture(db.Model):
	__tablename__ = "pictures"
	id = db.Column(db.Integer, primary_key=True)
	uid = db.Column(db.Integer, db.ForeignKey('users.id'))
	url = db.Column(db.String)
	profile_picture = db.Column(db.Boolean, default=False)

	@classmethod
	def add_pic(cls, uid, url, profile_picture=False):
		picture = cls(uid=uid,
					  url=url,
					  profile_picture=profile_picture
					  )
		db.session.add(picture)
		db.session.commit()
		return picture

	@classmethod
	def set_profile_pic(cls, uid, pic_id):
		Picture.query.filter_by(uid=uid).update({'profile_picture' : False})
		Picture.query.filter_by(id=pic_id, uid=uid).update({'profile_picture' : True})
		db.session.commit()

	def remove_pic(self):
		db.session.delete(self)
		db.session.commit()