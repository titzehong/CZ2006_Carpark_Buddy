from datetime import datetime
from carparkflask import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    saved_cps = db.relationship('User_saved_carparks', backref='creator', lazy=True)
    #posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Carpark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    carpark_name = db.Column(db.String(100), nullable=False)
    carpark_price = db.Column(db.Text, nullable=False)
    address = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    carpark_type = db.Column(db.String(50), default='None')
    type_of_parking_system = db.Column(db.String(50), default='None')
    short_term_parking = db.Column(db.String(50), default='None')
    free_parking = db.Column(db.String(50), default='None')
    night_parking = db.Column(db.String(50), default='None')
    carpark_decks = db.Column(db.Integer, default=1)
    gantry_heights = db.Column(db.Float, default=2)
    carpark_basement = db.Column(db.String(2), default='None')

    # Relationship wtih Carpark Times
    cp_times = db.relationship('Carpark_times', backref='cp_info', lazy=True)
    def __repr__(self):
        return f"Carpark('{self.carpark_name}', '{self.carpark_price}')"


class Carpark_times(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    update_datetime = db.Column(db.DateTime, nullable=False)

    day_of_week = db.Column(db.Integer, nullable=False)
    mins_of_day = db.Column(db.Integer, nullable=False)

    total_lots = db.Column(db.Integer, nullable=False)
    lot_type = db.Column(db.String(3))
    lots_available = db.Column(db.Integer, nullable=False)

    # Relationship with Carpark
    carpark_name = db.Column(db.String(100), db.ForeignKey('carpark.carpark_name'), nullable=False)
    def __repr__(self):
        return f"Carpark_time('{self.carpark_name}', '{self.update_datetime}')"


class User_saved_carparks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=False, nullable=False)
    saved_time = db.Column(db.DateTime, nullable=False)

    # Relationship with user table and carpark table
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    carpark_name = db.Column(db.String(100), db.ForeignKey('carpark.carpark_name'), nullable=False)

    def __repr__(self):
        return f"Saved_Carpark_Entry('{self.carpark_name}', '{self.saved_time}', '{self.email}')"