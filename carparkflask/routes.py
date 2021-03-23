
from flask import render_template, url_for, flash, redirect, request, request, Markup
import pandas as pd
from carparkflask import app, db, bcrypt
from carparkflask.plot_map import plot_map_from_postalCodes, plot_blank_map, get_forecast_plot, get_closest_avail
from carparkflask.forms import RegistrationForm, LoginForm, UpdateAccountForm, SearchCarparkForm
from carparkflask.models import User, Carpark, Carpark_times, User_saved_carparks
from flask_login import login_user, current_user, logout_user, login_required
from carparkflask.carpark_maps_utils import nearest_carPark, df_to_dict
import secrets
import os


@app.route('/', methods=['GET','POST'])
@app.route('/home', methods=['GET','POST'])  # extra decorator for more routes
def home():

    return render_template('home.html')


@app.route('/about')
def about():
	return render_template('about.html', title='About Test')


@app.route('/register', methods=['GET','POST'])
def register():

	if current_user.is_authenticated:
		return redirect(url_for('home'))

	form = RegistrationForm()

	if form.validate_on_submit():
		# Hash password
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		# Create user object
		user = User(username=form.username.data, email=form.email.data, password=hashed_password)

		# Ad to db
		db.session.add(user)
		db.session.commit()

		# Show success
		flash(f'Account Created for {form.username.data}', 'success')

		return redirect(url_for('login'))

	return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET','POST'])
def login():

	# Prevents access
	if current_user.is_authenticated:
		return redirect(url_for('home'))


	form = LoginForm()

	if form.validate_on_submit():
		
		# Get user and password
		user = User.query.filter_by(email=form.email.data).first()

		if user and bcrypt.check_password_hash(user.password, form.password.data):
			# Log them in with flask login extension
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')  # use get for access to prevent error
			# next page allows us to auto redirect to accounts page
			if next_page != None:
				next_page = next_page.replace('/',"")  # HACK
			return redirect(url_for(next_page)) if next_page else redirect(url_for('home'))

		else:
			flash('Login Unsuccessful. Please check email and password', 'danger')

	return render_template('login.html', title='Login', form=form)


@app.route('/map')
def map():
	print("HERE: ", postal1)
	print("STARTING Plot")
	plot_map_from_postalCodes([postal1, postal2, postal3], 'templates/map.html')
	print("ENDING Plot")
	return render_template('map.html')


@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('home'))

def save_picture(form_picture):
	# Saving users uploaded to file system
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
	form_picture.save(picture_path)

	return picture_fn


@app.route('/account', methods=['GET','POST'])
@login_required  # Makes this route only available after logging in
def account():

	form = UpdateAccountForm()

	if form.validate_on_submit():

		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			current_user.image_file = picture_file
		# Update username and email 
		current_user.username = form.username.data 
		current_user.email = form.email.data 
		db.session.commit()
		print("updated")
		flash('Your account has been updated!', 'success')
		return redirect(url_for('account'))  # POST GET Redirect pattern

	elif request.method == 'GET':

		form.username.data = current_user.username
		form.email.data = current_user.email
	image_file = url_for('static', filename='profile_pics/'+ current_user.image_file)
	return render_template('account.html', title='Account', image_file=image_file, form=form)


@app.route('/search', methods=['GET','POST'])
def search():

	# Generate html
	display_carparks=False
	html_map = plot_blank_map()
	# Convert to markup
	html_map = Markup(html_map)

	form = SearchCarparkForm()
	if form.validate_on_submit():
		#flash("Search Success", 'success')

		location_data = form.carpark.data
		# Query database for next 5 nearest carparks
		display_carparks=True

		#### Get top 5 carparks ####
		# Import the whole carpark table (not the best way to do it but nvm)
		all_carpark_df = pd.read_sql_table('carpark', db.engine)
		print("NUM CARPARKS: ", len(all_carpark_df))
		print("Detected Postal: ", location_data)
		top_carparks = nearest_carPark(location_data, all_carpark_df)

		# Get the times
		top_carpark_names = list(top_carparks['carpark_name'].values)
		print("TOP CP Names: ", top_carpark_names)
		# Query the times for it
		cp_times_query = Carpark_times.query.filter(Carpark_times.carpark_name.in_(top_carpark_names))
		cp_times = pd.read_sql(cp_times_query.statement, db.engine)

		# Get current date time
		current_dt = pd.datetime.now()
		# Round datetime to nearest 5mins
		current_min = current_dt.minute 
		rounded_min = current_min + (5 - current_min%5)
		if rounded_min == 60:
			rounded_min=55
		
		current_dt = current_dt.replace(minute=rounded_min)
		cp_times_df = get_closest_avail(current_dt, cp_times)

		# Join together and make column names correct # TODO after bjj
		cp_times_latest = cp_times_df[['carpark_name','update_datetime','total_lots','lots_available']]
		top_carparks_all_info = top_carparks.merge(cp_times_latest, on='carpark_name', how='left')
		print("SEARCH PAGE CARPARK INFO: ",top_carparks_all_info.head())

		try:
			top_carparks_all_info['update_datetime'] = top_carparks_all_info['update_datetime'].dt.round('1s')
		except:
			print('wtv')
		# Cant do this cause nans
		#top_carparks_all_info['lots_available'] = top_carparks_all_info['lots_available'].astype('int')
		#top_carparks_all_info['total_lots'] = top_carparks_all_info['total_lots'].astype('int')
		#print(top_carparks_all_info.columns)

		html_map = plot_map_from_postalCodes([location_data], top_carparks)
		html_map = Markup(html_map)
		return render_template('search.html', title='Search', form=form,
							    html_map = html_map, carparks=df_to_dict(top_carparks_all_info), display_carparks=display_carparks)

	return render_template('search.html', title='Search',
	  					    form=form, html_map = html_map, display_carparks=False)


# Fake page to help reroute checkbox data back to home
@app.route('/search_reroute', methods=['GET', 'POST'])
def search_reroute():
	if request.method == 'POST':
		print(request.form.getlist('save_checkbox'))
		print("SAVE IS WORKING HERERERE")

	submitted = request.form.get('submmited')
	saved_boxes = request.form.getlist('save_checkbox')
	print("WHAT IS IN savecheckbox?? :", saved_boxes)
	# If user is authenticated then save
	if submitted:
		print("SUBMISSSSIOSNSS")
		if current_user.is_authenticated:

			if len(saved_boxes) == 0:
				flash('No Carparks Selected!', 'danger')
				return redirect(url_for('saved_carparks'))
			# Update Database
			else:
				curr_username = current_user.username
				curr_email = current_user.email
				curr_savedtime = pd.datetime.now()
				curr_userid = current_user.id

				for cp_name in saved_boxes:
					user_saved_cp = User_saved_carparks(username=curr_username,
														email=curr_email,
														saved_time=curr_savedtime,
														user_id=curr_userid,
														carpark_name=cp_name)
					db.session.add(user_saved_cp)
				db.session.commit()

				flash('Carpark Saved!', 'success')
				return redirect(url_for('saved_carparks'))

		# Not logged in so flash a failed message
		else:
			flash('You must be logged in for that!', 'danger')
			return redirect(url_for('home'))

	return render_template('search_reroute.html', output_message=output_message)


@app.route('/saved_carparks', methods=['GET','POST'])
@login_required
def saved_carparks():

	# Get current Users carpark
	saved_cp_query = User_saved_carparks.query.filter(User_saved_carparks.email == current_user.email)
	saved_cp_frame = pd.read_sql(saved_cp_query.statement, db.engine)
	print("LENGTH SAVED CP: ", len(saved_cp_frame))

	if len(saved_cp_frame) == 0:
		# Return a Page saying no saved carparks
		return render_template('saved_carparks_blank.html')

	# Query carpark dataframe for carpark info of saved user carparks
	saved_cps = list(saved_cp_frame['carpark_name'].unique())
	all_carpark_df = pd.read_sql_table('carpark', db.engine)
	user_carparks_df = all_carpark_df[all_carpark_df['carpark_name'].isin(saved_cps)]


	# Get the available times and join together
	cp_times_query = Carpark_times.query.filter(Carpark_times.carpark_name.in_(saved_cps))
	cp_times = pd.read_sql(cp_times_query.statement, db.engine)

	# Get current date time
	current_dt = pd.datetime.now()
	# Round datetime to nearest 5mins
	current_min = current_dt.minute 
	rounded_min = current_min + (5 - current_min%5)
	if rounded_min == 60:
		rounded_min=55
	
	current_dt = current_dt.replace(minute=rounded_min)
	cp_times_df = get_closest_avail(current_dt, cp_times)

	# Join together and make column names correct # TODO after bjj
	cp_times_latest = cp_times_df[['carpark_name','update_datetime','total_lots','lots_available']]
	top_carparks_all_info = user_carparks_df.merge(cp_times_latest, on='carpark_name', how='left')
	top_carparks_all_info['update_datetime'] = top_carparks_all_info['update_datetime'].dt.round('1s')

	# Plot Map
	html_map = plot_map_from_postalCodes([], user_carparks_df)
	html_map = Markup(html_map)

	return render_template('saved_carparks.html',html_map=html_map, carparks=df_to_dict(top_carparks_all_info))


# Fake page to help reroute checkbox data back to home
@app.route('/saved_carparks_reroute', methods=['GET', 'POST'])
def saved_carparks_reroute():
	if request.method == 'POST':
		print(request.form.getlist('remove_checkbox'))
		print("REMOVE IS WORKING HERERERE")

	submitted = request.form.get('submmited')
	removed_boxes = request.form.getlist('remove_checkbox')
	print("WHAT IS IN savecheckbox?? :", removed_boxes)
	# If user is authenticated then save
	if submitted:
		print("SUBMISSSSIOSNSS")
		if current_user.is_authenticated:

			if len(removed_boxes) == 0:
				flash('No Carparks Selected!', 'danger')
				return redirect(url_for('saved_carparks'))
			# Update Database to remove entry
			else:
				curr_username = current_user.username
				curr_email = current_user.email
				curr_userid = current_user.id

				# Query the stuff
				to_delete = User_saved_carparks.query.filter(User_saved_carparks.carpark_name.in_(removed_boxes),
												User_saved_carparks.username==curr_username,
												User_saved_carparks.user_id==curr_userid).delete(synchronize_session='fetch')
				

				db.session.commit()

				flash('Carpark Removed!', 'success')
				return redirect(url_for('saved_carparks'))

		# Not logged in so flash a failed message
		else:
			flash('You must be logged in for that!', 'danger')
			return redirect(url_for('home'))

	return render_template('search_reroute.html', output_message=output_message)



# Used to display forecast chart and general statistics about carpark
@app.route('/carpark_info/<int:carpark_id>')
def carpark_info(carpark_id):

	# Query the carpark info from Carpark Table
	carpark = Carpark.query.get_or_404(carpark_id)
	# Get the latest datetime
	cp_times_query = Carpark_times.query.filter(Carpark_times.carpark_name == carpark.carpark_name)
	cp_times = pd.read_sql(cp_times_query.statement, db.engine)


	# Get current date time
	current_dt = pd.datetime.now()
	# Round datetime to nearest 5mins
	current_min = current_dt.minute 
	rounded_min = current_min + (5 - current_min%5)
	if rounded_min == 60:
		rounded_min=55
	current_dt = current_dt.replace(minute=rounded_min, second=0)
	cp_times_df = get_closest_avail(current_dt, cp_times)

	print("CURRENT DT: ", current_dt)
	forecastplot_html = get_forecast_plot(cp_times, carpark.carpark_name, current_dt)
	forecastplot_html = Markup(forecastplot_html)

	print("CP TIMES: ", df_to_dict(cp_times_df))
	cp_times_df['update_datetime'] = cp_times_df['update_datetime'].dt.round('1s')

	# Add Saving carpark time
	return render_template('carpark_page.html', title=carpark.carpark_name,
	 carpark=carpark, carpark_time_info=df_to_dict(cp_times_df)[0], html_forecast=forecastplot_html)
