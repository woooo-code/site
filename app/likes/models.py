# app/likes/models.py
from app import db

class Like(db.Model):
	__tablename__ = "likes"
	id = db.Column(db.Integer, primary_key=True)
	liked_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	liked_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))

	@classmethod
	def like_user(cls, liked_id, liked_by_id):
		like = cls(
				liked_id = liked_id,
				liked_by_id = liked_by_id
				)
		db.session.add(like)
		db.session.commit()
		return like
		
	@staticmethod
	def get_like_action(liked_id, liked_by_id):
		like_count = Like.query.filter_by(liked_id=liked_id, liked_by_id=liked_by_id).count()
		if like_count > 0:
			return "Unlike"
		return "Like"

	def remove_like(self):
		db.session.delete(self)
		db.session.commit()