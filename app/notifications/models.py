#app/notifications/models.py
from app import db
from flask import current_app
from datetime import datetime

class Notification(db.Model):
	__tablename__ = "notifications"

	id = db.Column(db.Integer, primary_key=True)
	owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	sent_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	event_id = db.Column(db.Integer)
	time_sent = db.Column(db.DateTime)

	@classmethod
	def create_notification(cls, owner_id, sent_by_id, event_id, time_sent):
		notification = cls(
			owner_id = owner_id,
			sent_by_id = sent_by_id,
			event_id = event_id,
			time_sent = time_sent
		)
		db.session.add(notification)
		db.session.commit()
		return notification

	def update_notification(self):
		self.time_sent = datetime.now()
		db.session.add(self)
		db.session.commit()

	def remove_notification(self):
		db.session.delete(self)
		db.session.commit()