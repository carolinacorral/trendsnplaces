# -*- coding: utf-8 -*-
"""
Created on Mon May 15 14:30:21 2023
Repository : https://github.com/carolinacorral/trendsnplaces

@author: Carolina Corral 
"""
from pytrends.request import TrendReq
import pandas as pd
import requests
from geopy.geocoders import Nominatim
import time 
import seaborn as sns
import matplotlib.pyplot as plt

pytrend = TrendReq()
# specify the keyword, geo code, and time frame (optional)
keyword = ['chiropractor']
geo = 'US-NY'

# Build the payload
pytrend.build_payload(kw_list=keyword, geo=geo)

# Retrieve the interest over time data and store it in a DataFrame
interest_df = pytrend.interest_by_region() 

loc_df = interest_df.reset_index(drop=False)

# Replace YOUR_API_KEY with your actual API key
API_KEY = 'YourAPIKey'

# Define the search parameters
params = {
    'key': API_KEY,
    'query': 'chiropractor', # replace with your desired keyword
    'location': '40.7484,-73.9857', # latitude and longitude of New York City
    'radius': 10 
}


# Function to get the latitude and longitude of a location using geopy
def get_lat_long(location):
    # Use geopy to get the latitude and longitude of the given location
    geolocator = Nominatim(user_agent="http")
    location = geolocator.geocode(location)
    if location is not None:
        return (location.latitude, location.longitude)
    else:
        return (None, None)


# Add two new columns to the dataframe for the latitude and longitude values
loc_df['latitude'] = 0.0
loc_df['longitude'] = 0.0

# Loop through each row in the dataframe
for index, row in loc_df.iterrows():
    # Get the latitude and longitude of the current row's geoName using geopy
    location = row['geoName']
    lat, long = get_lat_long(location)
    
    # Update the latitude and longitude values in the dataframe
    loc_df.at[index, 'latitude'] = lat
    loc_df.at[index, 'longitude'] = long
          
 
def get_num_results(latitude, longitude):
    if latitude is None or longitude is None:
      return None
 
    # Define the search parameters
    params = {
        'key': API_KEY,
        'query': 'chiropractic clinic', # replace with your desired keyword
        'location': f'{latitude},{longitude}', # latitude and longitude of the current row
        'radius': 10, #Desired radius
        'minrating': 3, # minimum rating score
    }

    
    # Send a GET request to the Places API
    response = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json', params=params)

    # Retrieve the number of places returned by the search
    results = response.json()
    num_places = len(results['results'])

    while 'next_page_token' in results:
        # Sleep for a few seconds to allow the next page to become available
        time.sleep(2)

        # Define the search parameters with the pagetoken parameter to fetch the next page
        params['pagetoken'] = results['next_page_token']

        # Send a GET request to the Places API to fetch the next page of results
        response = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json', params=params)

        # Retrieve the number of places returned by the search
        results = response.json()
        num_places += len(results['results'])


    return num_places

# Create an empty dataframe to store the results
results_df = pd.DataFrame(columns=['geoName', 'num_results'])

# Loop through each row in the dataframe and get the number of search results
for index, row in loc_df.iterrows():
    # Get the latitude and longitude of the current row
    latitude = row['latitude']
    longitude = row['longitude']

    # Get the number of search results from the Places API
    num_results = get_num_results(latitude, longitude)    

    # Add the location name and number of search results to the results dataframe
    results_df.loc[index] = [row['geoName'], num_results]


# Find the maximum value of "num_results"
max_num_results = results_df['num_results'].max()

# Calculate the percentages
results_df['percentage'] = (results_df['num_results'] / max_num_results) * 100


# Merge the 'num_results' column from results_df into loc_df based on 'geoName'
merged_df = loc_df.merge(results_df[['geoName', 'num_results']], on='geoName')


# Calculate the division between 'num_results' and 'chiropractor' 
merged_df['division'] = (merged_df['num_results'] / merged_df['chiropractor']).round(2)

# Create a heat map using seaborn
plt.figure(figsize=(12, 8))
sns.heatmap(merged_df.pivot(index='geoName', columns='division', values='division'),
            cmap='RdYlGn', vmin=0, vmax=merged_df['division'].max(), annot=True, fmt='.2f')
plt.title('Relation between interest and availability for Chiropractors')
plt.xlabel('Division')
plt.ylabel('geoName')
plt.show()