from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from carparkflask.models import User

class RegistrationForm(FlaskForm):
	username = StringField('Username',
							validators=[DataRequired(), Length(min=2, max=20)])

	email = StringField("Email",
						validators=[DataRequired(), Email()])

	password = PasswordField('Password', validators=[DataRequired()])

	confirmed_password = PasswordField('Confirm Password',
										validators=[DataRequired(), EqualTo('password')])

	submit = SubmitField('Sign Up')

	def validate_username(self, username):  # Check if user already exists in databse

		# Check whether user in databse
		user = User.query.filter_by(username=username.data).first()

		if user:
			raise ValidationError('Username is already taken. Please choose a different one')

	def validate_email(self, email):  # Check if user already exists in databse

		# Check whether user in databse
		user = User.query.filter_by(email=email.data).first()

		if user:
			raise ValidationError('Email is already taken. Please choose a different one')
	

class LoginForm(FlaskForm):
	#username = StringField('Username',
	#						validators=[DataRequired(), Length(min=2, max=20)])

	email = StringField("Email",
						validators=[DataRequired(), Email()])

	password = PasswordField('Password', validators=[DataRequired()])
	remember = BooleanField("Remember Me")
	submit = SubmitField('Login')



class UpdateAccountForm(FlaskForm):
	username = StringField('Username',
							validators=[DataRequired(), Length(min=2, max=20)])

	email = StringField("Email",
						validators=[DataRequired(), Email()])

	picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
	#password = PasswordField('Password', validators=[DataRequired()])

	submit = SubmitField('Update')

	def validate_username(self, username):  # Check if user already exists in databse

		if username.data != current_user.username:
			# Check whether user in databse
			user = User.query.filter_by(username=username.data).first()

			if user:
				raise ValidationError('Username is already taken. Please choose a different one')

	def validate_email(self, email):  # Check if user already exists in databse

		# Check whether user in databse
		if email.data != current_user.email:
			user = User.query.filter_by(email=email.data).first()

			if user:
				raise ValidationError('Email is already taken. Please choose a different one')



class SearchCarparkForm(FlaskForm):
	"""
	This form takes in the user's postal code and returns the top K nearest carpark
	"""
	carpark = StringField('Starting Location (Postal Code)', validators=[DataRequired()])
	submit = SubmitField('Search')
