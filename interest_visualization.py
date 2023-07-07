# -*- coding: utf-8 -*-
"""
Created on Mon May 15 14:30:21 2023
Repository : https://github.com/carolinacorral/trendsnplaces

@author: Carolina Corral 

"""

from pytrends.request import TrendReq
import pandas as pd
import requests
from adjustText import adjust_text
from geopy.geocoders import Nominatim
import time 
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf as pdf

pytrend = TrendReq()
# specify the keyword, geo code, and time frame (optional)
keyword = 'dog park' 
geo = 'US-CA'

# Replace YOUR_API_KEY with your actual API key
API_KEY = 'YOUR_API_KEY'

# Build the payload
pytrend.build_payload(kw_list=[keyword], geo=geo)

# Retrieve the interest over time data and store it in a DataFrame
interest_df = pytrend.interest_by_region() 

loc_df = interest_df.reset_index(drop=False)


# Function to get the latitude and longitude of a location using geopy
def get_lat_long(location):
    # Use geopy to get the latitude and longitude of the given location
    geolocator = Nominatim(user_agent="http")
    location = geolocator.geocode(location,timeout=None)
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
          
 #Function to get number of results
def get_num_results(latitude, longitude):
    if latitude is None or longitude is None:
      return None
 
   
    params = {
        'key': API_KEY,
        'query': keyword, 
        'location': f'{latitude},{longitude}',
        'radius': 10, #Desired radius
        'minrating': 3, # minimum rating score
    }

    
    # Send a GET request to the Places API
    response = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json', params=params)

    # Retrieve the number of places returned by the search
    results = response.json()
    num_places = len(results['results'])

    #Loop to retrieve more results if there are more than 20 available
    while 'next_page_token' in results:
        
        time.sleep(2)

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
    
    latitude = row['latitude']
    longitude = row['longitude']

    
    num_results = get_num_results(latitude, longitude)    

    # Add the location name and number of search results to the results dataframe
    results_df.loc[index] = [row['geoName'], num_results]


# Find the maximum value of "num_results"
max_num_results = results_df['num_results'].max()

# Calculate the percentages
results_df['percentage'] = (results_df['num_results'] / max_num_results) * 100


# Merge the 'num_results' column from results_df into loc_df based on 'geoName'
merged_df = loc_df.merge(results_df[['geoName', 'num_results']], on='geoName')

merged_df = merged_df[merged_df[keyword] != 0]

# Calculate the division between 'num_results' and 'chiropractor' 
merged_df['division'] = merged_df.apply(lambda row: round(row['num_results'] / row[keyword], 2), axis=1)


# Create a heat map using seaborn
heat_map = plt.figure(figsize=(12, 8))
sns.heatmap(merged_df.pivot(index='geoName', columns='division', values='division'),
            cmap='RdYlGn', vmin=0, vmax=merged_df['division'].max(), annot=True, fmt='.2f')

plt.title('Relation between interest and availability')
plt.xlabel('Number of results to popularity ratio')
plt.ylabel('City Name')

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


# Sort the dataframe by interest value in descending order
sorted_by_interest = merged_df.sort_values(keyword, ascending=False)

# Sort the dataframe by num_places value in descending order
sorted_by_num_places = merged_df.sort_values('num_results', ascending=False)

# Histogram of interest values
interest_rank = plt.figure(figsize=(10,6))
plt.barh(sorted_by_interest['geoName'], sorted_by_interest[keyword])
plt.xlabel('Place',wrap=True)
plt.ylabel('Interest Value')
plt.title('Places Ranked by Interest')
plt.xticks(rotation=90)

# Histogram of num_places values
nums_rank = plt.figure(figsize=(10,6))
plt.barh(sorted_by_num_places['geoName'], sorted_by_num_places['num_results'])
plt.xlabel('Place',wrap=True)
plt.ylabel('Number of Places')
plt.title('Places Ranked by Number of Results')
plt.xticks(rotation=90)

# Create a PDF object
pdf_file = pdf.PdfPages('C:/Users/Carolina/proyc/metodos/trends/results/results.pdf')

# Add each plot to the PDF file
pdf_file.savefig(sct, bbox_inches='tight')
pdf_file.savefig(sct_no_name, bbox_inches='tight')
pdf_file.savefig(interest_rank, bbox_inches='tight')
pdf_file.savefig(nums_rank, bbox_inches='tight')
# Add more plots as needed

# Close the PDF file
pdf_file.close()

