from flask import Flask, render_template, url_for, flash, redirect, request
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm, LoginForm
from plot_map import plot_map_from_postalCodes
#from models import User, Carpark

app = Flask(__name__)
app.config['SECRET_KEY'] = "78e0e324b44e5c7d364d4fe1a2c8dbcf"  # Make safe
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
"""
import secrets
secrets.token_hex(16)  # to generate random string as secret key, make environment variable  
"""


# Dummy data
carparks = [
	{
		'cp_name':'Punggol Park Carpark 1A',
		'cp_avail':'20',
		'price': '$1',
		'date_last_checked':'April 20, 2021, 13:10'
	},

	{
		'cp_name':'Bishan Carpark Block 132',
		'cp_avail':'23',
		'price': '$2',
		'date_last_checked':'April 21, 2021. 13:11'
	}
]


@app.route('/', methods=['GET','POST'])
@app.route('/home', methods=['GET','POST'])  # extra decorator for more routes
def home():

    if request.method == "POST":

        req = request.form
        print(req)

        global postal1
        postal1 = req.get("postal1")
        global postal2
        postal2 = req.get('postal2')
        global postal3
        postal3 = req.get('postal3')

        print('POSTAL: ', postal1)
        return redirect(request.url)

    return render_template('home.html', carparks=carparks)


@app.route('/about')
def about():
	return render_template('about.html', title='About Test')


@app.route('/register', methods=['GET','POST'])
def register():
	form = RegistrationForm()

	if form.validate_on_submit():
		flash(f'Account Created for {form.username.data}', 'success')
		return redirect(url_for('home'))

	return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET','POST'])
def login():
	form = LoginForm()

	if form.validate_on_submit():
		if form.email.data == 'admin@blog.com' and form.password.data == 'password':
			flash('you have been logged in!', 'success')
			return redirect(url_for('home'))

		else:
			flash('Login Unsuccessful. Please check username and password', 'danger')
	return render_template('login.html', title='Login', form=form)

@app.route('/map')
def map():


	print("HERE: ", postal1)
	print("STARTING Plot")
	plot_map_from_postalCodes([postal1, postal2, postal3], 'templates/map.html')
	print("ENDING Plot")
	return render_template('map.html')

# Run app directly from python script (or can use shell with flask run)
if __name__ == '__main__':
	app.run(debug=True)