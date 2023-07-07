from pytrends.request import TrendReq
import pandas as pd
import requests
from adjustText import adjust_text
from geopy.geocoders import Nominatim
import time 
import matplotlib.pyplot as plt


def get_lat_long(location):
    geolocator = Nominatim(user_agent="http")
    try:
        location = geolocator.geocode(location, timeout=None)
        if location is not None:
            return location.latitude, location.longitude
    except:
        print("Geocoding service is unavailable. Unable to retrieve latitude and longitude.")
    return None, None

def get_num_results(latitude, longitude, API_KEY,keyword):
    if latitude is None or longitude is None:
        return None
    params = {
        'key': API_KEY,
        'query': keyword, 
        'location': f'{latitude},{longitude}',
        'radius': 10, #Desired radius
        'minrating': 3, # minimum rating score
    }

    response = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json', params=params)

    results = response.json()
    num_places = len(results['results'])

    while 'next_page_token' in results:  
        time.sleep(2)
        params['pagetoken'] = results['next_page_token']
        response = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json', params=params) 
        results = response.json()
        num_places += len(results['results'])

    return num_places

def generate_graphs(keyword,geo,API_KEY):
    pytrend = TrendReq()

    pytrend.build_payload(kw_list=[keyword], geo=geo)

    interest_df = pytrend.interest_by_region() 

    loc_df = interest_df.reset_index(drop=False)

    loc_df['latitude'] = 0.0
    loc_df['longitude'] = 0.0

    for index, row in loc_df.iterrows():
        location = row['geoName']
        lat, long = get_lat_long(location)
        
        loc_df.at[index, 'latitude'] = lat
        loc_df.at[index, 'longitude'] = long
            
    results_df = pd.DataFrame(columns=['geoName', 'num_results'])

    for index, row in loc_df.iterrows():
        
        latitude = row['latitude']
        longitude = row['longitude']

        num_results = get_num_results(latitude, longitude,API_KEY,keyword)    

        results_df.loc[index] = [row['geoName'], num_results]


    
    max_num_results = results_df['num_results'].max()

    results_df['percentage'] = (results_df['num_results'] / max_num_results) * 100

    merged_df = loc_df.merge(results_df[['geoName', 'num_results']], on='geoName')

    merged_df = merged_df[merged_df[keyword] != 0]

    merged_df['division'] = merged_df.apply(lambda row: round(row['num_results'] / row[keyword], 2), axis=1)


    sct = plt.figure(figsize=(12,8))
    plt.scatter(merged_df[keyword], merged_df['num_results'])
    plt.xlabel('Interest')
    plt.ylabel('Number of places')
    plt.title('Interest vs Availability')
    labels= []
    for i, row in merged_df.iterrows():
        x_val = row[keyword]
        y_val = row['num_results']
        label = row['geoName']
        text = plt.text(x_val, y_val, label, ha='left', va='bottom')
        labels.append(text)
        
    adjust_text(labels, arrowprops=dict(arrowstyle='-', color='gray'))

    sct_no_name = plt.figure(figsize=(12,8))
    plt.scatter(merged_df[keyword], merged_df['num_results'])
    plt.xlabel('Interest')
    plt.ylabel('Number of places')
    plt.title('Interest vs Availability')

    sorted_by_interest = merged_df.sort_values(keyword, ascending=False)

    sorted_by_num_places = merged_df.sort_values('num_results', ascending=False)

    interest_rank = plt.figure(figsize=(10,6))
    plt.barh(sorted_by_interest['geoName'], sorted_by_interest[keyword])
    plt.xlabel('Place',wrap=True)
    plt.ylabel('Interest Value')
    plt.title('Places Ranked by Interest')
    plt.xticks(rotation=90)

    nums_rank = plt.figure(figsize=(10,6))
    plt.barh(sorted_by_num_places['geoName'], sorted_by_num_places['num_results'])
    plt.xlabel('Place',wrap=True)
    plt.ylabel('Number of Places')
    plt.title('Places Ranked by Number of Results')
    plt.xticks(rotation=90)
    
    plt.show()



