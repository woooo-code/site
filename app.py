from app import create_app, db, socketio

if __name__ == '__main__':
	flask_app = create_app('dev')
	with flask_app.app_context():
		db.create_all()
	socketio.run(flask_app)
