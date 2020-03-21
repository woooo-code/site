# app/blocks/models.py
from app import db

class Block(db.Model):
	__tablename__ = "blocks"
	id = db.Column(db.Integer, primary_key=True)
	blocked_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	blocked_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))

	@classmethod
	def create_block(cls, b_id, b_b_id):
		block = cls(
			blocked_id = b_id,
			blocked_by_id = b_b_id
		)
		db.session.add(block)
		db.session.commit()
		return block

	def remove_block(self):
		db.session.delete(self)
		db.session.commit()