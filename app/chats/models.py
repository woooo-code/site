# app/chats/models.py
from app import db
from datetime import datetime

class Chat(db.Model):
	__tablename__ = "chats"
	id = db.Column(db.Integer, primary_key=True)
	sent_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	received_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	message = db.Column(db.String(500))
	message_time = db.Column(db.String(50))

	@classmethod
	def save_message(cls, sent_by_id, received_by_id, message, message_time):
		message = cls(sent_by_id=sent_by_id,
						received_by_id=received_by_id,
						message=message,
						message_time=message_time)
		db.session.add(message)
		db.session.commit()
		return message
