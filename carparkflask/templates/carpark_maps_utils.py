import pandas as pd
import simplejson as json
import time
import requests
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from vincenty import vincenty


#get the hdb carpark info from govtech api and write it into a csv file
def get_hdb_cp_response():
    hdb_cp_response = requests.get("https://data.gov.sg/api/action/datastore_search?resource_id=139a3035-e624-4f56-b63f-89ae28d4ae4c&limit=10000")
    print(hdb_cp_response.status_code)
    hdb_dict = json.loads(hdb_cp_response.text)
    dict = hdb_dict['result']['records']
    hdb_cp_df = pd.DataFrame(dict)
    
    # api token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOjcyNzMsInVzZXJfaWQiOjcyNzMsImVtYWlsIjoibW9qdW55aTIzQGdtYWlsLmNvbSIsImZvcmV2ZXIiOmZhbHNlLCJpc3MiOiJodHRwOlwvXC9vbTIuZGZlLm9uZW1hcC5zZ1wvYXBpXC92MlwvdXNlclwvc2Vzc2lvbiIsImlhdCI6MTYxNDY2MjkzOCwiZXhwIjoxNjE1MDk0OTM4LCJuYmYiOjE2MTQ2NjI5MzgsImp0aSI6ImRkMjZjMGQ2OWUyNjQwYTc5OWM1MGJmM2EwMjIxMDlhIn0._BQm_K8VWKAXSwgt7JNq0m59ltDypR4LybjIH3zgdb8
    # expiry: 5th March 2021, 1:28:58 pm UTC+08:00  
    
    info = [str(hdb_cp_df['x_coord'][i]+ "," + hdb_cp_df['y_coord'][i]) for i in range(len(hdb_cp_df))]
    long = [] #x-coord
    lat = [] #y-coord
    postalLst = []

    for i in range(len(info)):
            req=requests.get('https://developers.onemap.sg/privateapi/commonsvc/revgeocodexy?location='+ info[i] +'&token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOjcyNzMsInVzZXJfaWQiOjcyNzMsImVtYWlsIjoibW9qdW55aTIzQGdtYWlsLmNvbSIsImZvcmV2ZXIiOmZhbHNlLCJpc3MiOiJodHRwOlwvXC9vbTIuZGZlLm9uZW1hcC5zZ1wvYXBpXC92MlwvdXNlclwvc2Vzc2lvbiIsImlhdCI6MTYxNDY2MjkzOCwiZXhwIjoxNjE1MDk0OTM4LCJuYmYiOjE2MTQ2NjI5MzgsImp0aSI6ImRkMjZjMGQ2OWUyNjQwYTc5OWM1MGJmM2EwMjIxMDlhIn0._BQm_K8VWKAXSwgt7JNq0m59ltDypR4LybjIH3zgdb8&buffer=100&addressType=all', timeout=2)
            jdata = json.loads(req.text)
            if len(jdata['GeocodeInfo'])>=1:
                long.append(jdata['GeocodeInfo'][0]['LONGITUDE'])
                lat.append(jdata['GeocodeInfo'][0]['LATITUDE'])
                postalLst.append(jdata['GeocodeInfo'][0]['ADDRESS'])
            else:
                long.append(None)
                lat.append(None)
                postalLst.append(None)
    
    hdb_cp_df['longitude'] = long
    hdb_cp_df['latitude'] = lat
    hdb_cp_df['postal'] = postalLst
    #hdb_cp_df.to_csv (r'C:\Users\mjyco\Desktop\CZ2006 Project\x\hdb_carPark_full_info.csv', index = False, header=True)

    return hdb_cp_df


# get the carpark info from lta (since it is a static set, lta site didnt use api for this.) and write it into a csv file
def get_lta_cp_response():
    lta_cp_df =  pd.read_csv(r'C:\Users\mjyco\Desktop\CZ2006 Project\x\CarParkRates.csv')
    lta_long = []
    lta_lat = []
    lta_x = []
    lta_y = []
    lta_postal = []
    
    for i in range(len(lta_cp_df)):
            req = requests.get('https://developers.onemap.sg/commonapi/search?searchVal='+str(lta_cp_df['CarPark'][i])+'&returnGeom=Y&getAddrDetails=Y&pageNum=1', timeout=1)
            jdata = json.loads(req.text)
            if jdata['found']>=1:
                lta_long.append(jdata['results'][0]['LONGITUDE'])
                lta_lat.append(jdata['results'][0]['LATITUDE'])
                lta_postal.append(jdata['results'][0]['POSTAL'])
                lta_x.append(jdata['results'][0]['X'])
                lta_y.append(jdata['results'][0]['Y'])
            else:
                lta_long.append(None)
                lta_lat.append(None)
                lta_postal.append(None)
                lta_x.append(None)
                lta_y.append(None)

    lta_cp_df['longitude'] = lta_long
    lta_cp_df['latitude'] = lta_lat
    lta_cp_df['postal'] = lta_postal
    lta_cp_df['x_coord'] = lta_x
    lta_cp_df['y_coord'] = lta_y
    
    #lta_cp_df.to_csv (r'C:\Users\mjyco\Desktop\CZ2006 Project\x\lta_carPark_full_info.csv', index = False, header=True)

    return lta_cp_df

#Combining hdb carpark info from govtech with carpark info from lta
def full_cp_response():
    hdb_cp_df = get_hdb_cp_response()
    lta_cp_df = get_lta_cp_response()
#    hdb_cp_df = pd.read_csv('C:\Users\mjyco\Desktop\CZ2006 Project\x\hdb_carPark_full_info.csv')
#    lta_cp_df = pd.read_csv('C:\Users\mjyco\Desktop\CZ2006 Project\x\lta_carPark_full_info.csv')
    main_cp_df = pd.concat([hdb_cp_df, lta_cp_df], axis=1)
#    hdb_cp_df.to_csv (r'C:\Users\mjyco\Desktop\CZ2006 Project\x\hdb_carPark_full_info.csv', index = False, header=True)
#    lta_cp_df.to_csv (r'C:\Users\mjyco\Desktop\CZ2006 Project\x\lta_carPark_full_info.csv', index = False, header=True)
    #main_cp_df.to_csv (r'C:\Users\mjyco\Desktop\CZ2006 Project\x\carPark_full_info.csv', index = False, header=True)
    return main_cp_df



#Using the full CP df and the postal code that the user input, get back the nearest 10 carpark info
def nearest_carPark(postal, main_df):
    postal_long = ""
    postal_lat = ""
    req=requests.get('https://developers.onemap.sg/commonapi/search?searchVal='+postal+'&returnGeom=Y&getAddrDetails=Y&pageNum=1', timeout=1)
    jdata = json.loads(req.text)
    if jdata['found']>=1:
        postal_long = jdata['results'][0]['LONGITUDE']
        postal_lat = jdata['results'][0]['LATITUDE']
    
    for i in range(len(df)):
        check_long = main_df["longitude"][i]
        check_lat = main_df["latitude"][i]
        main_df["dist"] = vincenty( [float(postal_long),float(postal_lat)] , [float(check_long),float(check_lat)])
    
    sorted_df = main_df.sort_values(by=['dist'], ascending=True)
    nearest_df = sorted_df.iloc[0:10]

    return nearest_df
    


def plot_map_from_postalCodes(nearest_df, html_dir):
    df = nearest_df
    # Initialize figure
    fig = go.Figure()

    # Add Traces
    fig.add_trace(go.Scattermapbox(lat = df['latitude'], long = df['longitude'],
            name = "Car Park Locations", mode='markers',
            text = 'Address: '+df['Address'],
            marker = dict(color = 'red', size=10, opacity = 1)))
    
    # To create different tabs in the same graph

    fig.update_layout(
        legend=dict(x=0.7, y=1.0, bgcolor = 'white'),
        title = 'Carparks Map',
        autosize = True,
        margin=dict(t=30, b=10, l=30, r=0),
        hovermode='closest',
        mapbox=go.layout.Mapbox(
            accesstoken= 'pk.eyJ1IjoiYWRyaWFua2h5IiwiYSI6ImNrbG5meXhkcDBpdGoyd282dWt3eTVzOXMifQ.hrpDfYNEYranjKjXXHX0hg', # register an account with plotly and generate the API key
            bearing=0,
            center=go.layout.mapbox.Center(lat=1.3448,lon=103.8224),pitch=0,zoom=10.5))          

    # fig.show()
    fig.write_html(html_dir)
    return



def parse_carpark_json(carpark_json):
    queried_timestamp = carpark_json['items'][0]['timestamp']
    carpark_list = carpark_json['items'][0]['carpark_data']

    # Fix 
    carpark_list_cleaned = []

    for cp in carpark_list:

        cp_dict = {}
        cp_dict['carpark_number'] = cp['carpark_number']
        cp_dict['update_datetime'] = cp['update_datetime']
        cp_dict = {**cp_dict, **cp['carpark_info'][0]}
        carpark_list_cleaned.append(cp_dict)

    carpark_df = pd.DataFrame(carpark_list_cleaned)

    return carpark_df, queried_timestamp
    # Collect For many dates
"""
query = {'date_time':'2020-01-01T13:32:11'}
response = requests.get("https://api.data.gov.sg/v1/transport/carpark-availability", params=query)
print(response.json())

cp_df, t = parse_carpark_json(response.json())
print(cp_df.head())
"""