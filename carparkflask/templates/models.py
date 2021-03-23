from __main__ import db


class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	username = db.Column(db.String(20), unique=True, nullable=False)
	image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
	password = db.Column(db.String(60), nullable=False)

	carparks = db.relationship("carpark", backref='author', lazy=True)

	def __repr__(self):
		return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Carpark(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	carpark_name = db.Column(db.String(100), unique=True, nullable=False)
	price = db.Column(db.String(120), unique=True, nullable=False)

	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

	def __repr__(self):
		return f"Carpark('{self.carpark_name}', '{self.price}'"