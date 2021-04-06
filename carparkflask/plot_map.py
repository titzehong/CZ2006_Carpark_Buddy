import time
import requests
import simplejson as json
import pandas as pd
import plotly.express as px
from datetime import datetime, timezone
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.io import to_html
import numpy as np 

# https://stackoverflow.com/questions/37683147/getting-script-and-div-tags-from-plotly-using-python

def plot_map_from_postalCodes(PostalCodes, carpark_latlons):
    """
    PostalCodes: Single postal code of user
    carpark_latlons: Dataframe with two columns (lat,lon) for the queried carparks

    """
    PostalCodes = [str(i) for i in PostalCodes]
    LongLst = []
    LatLst = []
    AddressLst = []
    XLst = []
    YLst = []

    print("STARTING REQUESTS")
    start=time.time()
    for i in range(len(PostalCodes)):
        print(i)
        headers = {"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"}
        req=requests.get('https://developers.onemap.sg/commonapi/search?searchVal='+PostalCodes[i]+'&returnGeom=Y&getAddrDetails=Y&pageNum=1', headers=headers,timeout=5)
        jdata = json.loads(req.text)
        if jdata['found']>=1:
            LongLst.append(jdata['results'][0]['LONGITUDE'])
            LatLst.append(jdata['results'][0]['LATITUDE'])
            AddressLst.append(jdata['results'][0]['ADDRESS'])
            XLst.append(jdata['results'][0]['X'])
            YLst.append(jdata['results'][0]['Y'])
        else:
            LongLst.append(None)
            LatLst.append(None)
            AddressLst.append(None)
            XLst.append(None)
            YLst.append(None)
    print('Time Taken:',time.time()-start)  

    df = pd.DataFrame({'PostalCode': PostalCodes,
                      'Long': LongLst,
                      'Lat': LatLst,
                      'Address': AddressLst,
                      'X': XLst,
                      'Y': YLst})

    # Initialize figure
    fig = go.Figure()


    # Add Traces of User
    fig.add_trace(go.Scattermapbox(lat = df['Lat'], lon = df['Long'],
            name = "User Location", mode='markers',
            text = 'Address: '+df['Address'],
            marker = dict(color = 'red', size=10, opacity = 1)))

    # Add Traces of User
    fig.add_trace(go.Scattermapbox(lat = carpark_latlons['latitude'],lon = carpark_latlons['longitude'],
            name = "Car Park Locations", mode='markers',
            text = 'Address: '+carpark_latlons['address'],
            marker = dict(color = 'Blue', size=10, opacity = 1)))
    
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
    #fig.write_html(html_dir)
    out_html = to_html(fig, include_plotlyjs=False, full_html=False)
    return out_html


def plot_blank_map():

    # Initialize figure
    fig = go.Figure()

    # To create different tabs in the same graph
    fig.add_trace(go.Scattermapbox(lat = [1.3448],lon = [103.8224],
        name = "Car Park Locations", mode='markers',
        marker = dict(color = 'white', size=1, opacity = 0)))

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
    #fig.write_html(html_dir)
    out_html = to_html(fig, include_plotlyjs=False, full_html=False)
    return out_html


"""
def get_forecast_plot(agg_df, cp, selected_datetime):
    dow = selected_datetime.weekday()
    h = selected_datetime.hour
    m = selected_datetime.minute
    motd = h*60 + m

    cp_msk = agg_df['carpark_name'] == cp
    dow_msp = agg_df['day_of_week'] == dow

    temp = agg_df[cp_msk & dow_msp]

    selected_idx = np.where(temp['mins_of_day']==motd)[0][0]

    if selected_idx<10:
        left_idx = 0
        right_idx = 21

        left_highlight_idx = 0
        right_highlight_idx = selected_idx+5

    elif selected_idx>=temp.shape[0]-10:
        left_idx = temp.shape[0]-21
        right_idx = temp.shape[0]

        left_highlight_idx = selected_idx-5
        right_highlight_idx = temp.shape[0]

    else:
        left_idx = selected_idx-10
        right_idx = selected_idx+11

        left_highlight_idx = selected_idx-5
        right_highlight_idx = selected_idx+5    

    X = temp.iloc[left_idx:right_idx]['mins_of_day']
    Y = temp.iloc[left_idx:right_idx]['lots_available']

    X_highlight = temp.iloc[left_highlight_idx:right_highlight_idx]['mins_of_day']
    max_availability = Y.max()

    fig = go.Figure()
    fig = go.Figure(go.Scatter(x=X_highlight, y=[max_availability+5 for _ in range(len(X_highlight))], 
                               fill="tozeroy", marker = dict(size=1,
                                  line=dict(width=1,
                                            color='DarkSlateGrey'))))

    fig.add_trace(go.Scatter(x=X, y=Y,
                        mode='lines',
                        name='lines'))
#     fig.show()
    out_html = to_html(fig, include_plotlyjs=True, full_html=True)
    return out_html

"""

def get_forecast_idx(selected_idx, N):

    if selected_idx<10:
        left_idx = 0
        right_idx = 21

        left_highlight_idx = 0
        right_highlight_idx = selected_idx+5

    elif selected_idx>=N-10:
        left_idx = N-21
        right_idx = N

        left_highlight_idx = selected_idx-5
        right_highlight_idx = N

    else:
        left_idx = selected_idx-10
        right_idx = selected_idx+11

        left_highlight_idx = selected_idx-5
        right_highlight_idx = selected_idx+5

    return left_idx, right_idx, left_highlight_idx, right_highlight_idx

def get_forecast_plot(agg_df, cp, selected_datetime):
    dow = selected_datetime.weekday()
    h = selected_datetime.hour
    m = selected_datetime.minute
    motd = h*60 + m

    cp_msk = agg_df['carpark_name'] == cp
    dow_msp = agg_df['day_of_week'] == dow

    temp = agg_df[cp_msk & dow_msp]

    selected_idx = np.where(temp['mins_of_day']==motd)[0][0]

    N = temp.shape[0]

    left_idx, right_idx, left_highlight_idx, right_highlight_idx = get_forecast_idx(selected_idx, N)  

    X = temp.iloc[left_idx:right_idx]['mins_of_day']
    Y = temp.iloc[left_idx:right_idx]['lots_available']


    left_timeDelta = pd.timedelta_range(start='5 min', periods=selected_idx-left_idx, freq='5min')[::-1]
    right_timeDelta = pd.timedelta_range(start='0 day', periods=right_idx-selected_idx, freq='5min')
    X = [selected_datetime-td for td in left_timeDelta] + [selected_datetime+td for td in right_timeDelta]

    left_timeDelta = pd.timedelta_range(start='5 min', periods=selected_idx-left_highlight_idx, freq='5min')[::-1]
    right_timeDelta =pd.timedelta_range(start='0 day', periods=right_highlight_idx-selected_idx, freq='5min')
    X_highlight = [selected_datetime-td for td in left_timeDelta] + [selected_datetime+td for td in right_timeDelta]
    
    max_availability = Y.max()

    fig = go.Figure(go.Scatter(x=X_highlight, y=[max_availability+5 for _ in range(len(X_highlight))], 
                               fill="tozeroy", marker = dict(size=1,
                                  line=dict(width=1,
                                            color='DarkSlateGrey')),
                              name='Relevant Time Window'),
                   layout=go.Layout(
        title=go.layout.Title(text="Forecast availability on Date: {}".format(selected_datetime.strftime("%Y-%m-%d %H:%M")))
    ))
    

    fig.add_trace(go.Scatter(x=X, y=Y,
                        mode='lines',
                        name='Available Lots'))
    

    out_html = to_html(fig, include_plotlyjs=True, full_html=False)
    return out_html


def get_closest_avail(selected_datetime, agg_df):
    dow = selected_datetime.weekday()
    h = selected_datetime.hour
    m = selected_datetime.minute
    motd = h*60 + m
    
    dow_msp = agg_df['day_of_week'] == dow
    motd_msp = agg_df['mins_of_day'] == motd
    temp = agg_df[dow_msp & motd_msp]
    return temp