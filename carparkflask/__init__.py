from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


app = Flask(__name__)
app.config['SECRET_KEY'] = "78e0e324b44e5c7d364d4fe1a2c8dbcf"  # Make safe
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site17.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)  # Encrypts PW
login_manager = LoginManager(app)  # Handles sessions
login_manager.login_view = 'login'  # Pass in login route so that manager auto reroutes to login page when user tries to access acount page
login_manager.login_message_category = 'info'


from carparkflask import routes
from carparkflask.populate_db import populate_carpark_db, populate_carpark_times
from carparkflask.models import Carpark, Carpark_times
# Pop Carpark
pop_carpark_db = True
if pop_carpark_db:
	print("Populating DBs")
	if Carpark.query.first() is None:
		populate_carpark_db('hdb_carpark_info/carPark_main_info.csv')

	if Carpark_times.query.first() is None:
		populate_carpark_times('hdb_carpark_info/agg_df.csv')
