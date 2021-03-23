from carparkflask import db
from carparkflask.models import Carpark, Carpark_times
import pandas as pd
# Create user object
#user = User(username=form.username.data, email=form.email.data, password=hashed_password)

# Ad to db
#db.session.add(user)
#db.session.commit()

def populate_carpark_db(fp):

	carpark_static_db = pd.read_csv(fp)

	for row in carpark_static_db.itertuples():

		cp = Carpark(carpark_name=row.car_park_no,
					carpark_price=0,
					address=row.address,
					latitude=row.latitude,
					longitude=row.longitude,
					carpark_type=row.car_park_type,
					type_of_parking_system=row.type_of_parking_system,
					short_term_parking=row.short_term_parking,
					free_parking=row.free_parking,
					night_parking=row.night_parking,
					carpark_decks=row.car_park_decks,
					gantry_heights=row.gantry_height,
					carpark_basement=row.car_park_basement)

		db.session.add(cp)

	db.session.commit()
	print("Carpark DB Populated")
	return 


def populate_carpark_times(fp):

	carpark_times_db = pd.read_csv(fp)

	for i, row in enumerate(carpark_times_db.itertuples()):

		cp_time = Carpark_times(update_datetime=pd.datetime.now(),
								day_of_week=row.dayOfWeek,
								mins_of_day=row.minsOfTheDay,
								total_lots=row.total_lots,
								lot_type=row.lot_type,
								lots_available=row.lots_available,
								carpark_name=row.carpark_number)

		db.session.add(cp_time)
		#db.session.commit()
		if i%50000 == 0:
			db.session.commit()
			print('Record: ', i,'/',len(carpark_times_db))

	#db.session.commit()

	print("Carpark Times Populated")
	return