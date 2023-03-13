import os
import requests
import pandas as pd
import secrets_
import json
import numpy as np


def get_store_addresses(filename):
    # initialize vars
    url = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json'
    key = secrets_.google_key
    p = {
        'inputtype': 'textquery',
        'key': key,
        'fields': 'name,formatted_address,geometry',
        'locationbias': 'circle:645000@39.5501,105.7821' # bias for results in Colorado
        }

    i = 0

    # read existing data
    source_dir = os.path.dirname(__file__) #<-- directory name
    full_path = os.path.join(source_dir, filename)
    df = pd.read_csv(full_path)

    # initialize new var lists
    lat_list = []
    long_list = []
    name_list = []
    address_list = []

    for store in df.iterrows():
        # grab store info
        if store[1][1] > 0:
            p['input'] = f'{store[1][0]} {int(store[1][1])} {store[1][3]}, CO dispensary'
        else: # Oct 2017 data has no ZIP, so use city instead
            p['input'] = f'{store[1][1]} {store[1][3]} CO dispensary'

        # make Google Maps API request
        r = requests.get(url, params = p)
        j = json.loads(r.text)

        # parse JSON response and organize new info
        if j['status'] == 'ZERO_RESULTS':
            for list in [lat_list, long_list, name_list, address_list]:
                list.append(np.nan)
        else:
            try:
                lat_list.append(j['candidates'][0]['geometry']['location']['lat'])
                long_list.append(j['candidates'][0]['geometry']['location']['lng'])
                name_list.append(j['candidates'][0]['name'])
                address_list.append(j['candidates'][0]['formatted_address'])
            except: 
                print(j) # prints error rows -- helpful for debugging

        # print periodic progress updates
        i += 1
        if i % 20 == 0:
            print(f'finished {i} of {len(df)} records')
            print(f'{round(i / len(df) * 100, 2)}% done')

    # save new columns
    df['LAT'] = lat_list
    df['LONG'] = long_list
    df['google_name'] = name_list
    df['address'] = address_list

    # write to csv
    #df.to_csv('co_stores_addresses.csv', index = False)

    return df

def reformat_addresses(data):
    '''
    helper func to parse addresses to census geocoder format
    takes dataframe w/ address column
    writes as csv to passed filename
    returns None
    '''

    streets = []
    cities = []
    states = []
    zips = []

    for address in data.address:
        if address is not np.nan:
            a = address.split(',')
            streets.append(a[0])
            cities.append(a[1])
            states.append(a[2][:3])
            zips.append(a[2][-5:])

    addresses = pd.DataFrame()
    addresses['street'] = streets
    addresses['city'] = cities
    addresses['state'] = states
    addresses['zip'] = zips


    return addresses

def geocode_addresses(data):
    '''
    takes df w/ address column
    returns census geocoded addresses
    '''
    i = 0

    url = 'https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress'
    params = {'benchmark': 'Public_AR_Current',
              'vintage': 'ACS2022_Current',
              'format': 'JSON'}
    tracts = []
    counties = []
    x_coords = []
    y_coords = []


    for address in data.address:
        params['address'] = address
        r = requests.get(url, params = params)
        info = json.loads(r.text)
        match = info['result']['addressMatches']
        if len(match) > 0:
            tract = match[0]['geographies']['Census Tracts'][0]['BASENAME']
            county = match[0]['geographies']['Counties'][0]['BASENAME']
            x_coord = match[0]['coordinates']['x']
            y_coord = match[0]['coordinates']['y']

            tracts.append(tract)
            counties.append(county)
            x_coords.append(x_coord)
            y_coords.append(y_coord)

        else:
            for lst in (tracts, counties, x_coords, y_coords):
                lst.append(np.nan)

        # track progress
        i += 1
        if i % 20 == 0:
            print(f'finished geocoding {i} of {len(data)} addresses')
            print(f'{round(i / len(data) * 100, 2)}% done')

    data['tract'] = tracts
    data['county'] = counties
    data['x'] = x_coords
    data['y'] = y_coords

    return data    

def geocode_coords(data):

    counties = []
    tracts = []

    url = 'https://geo.fcc.gov/api/census/block/find'
    params = {'censusYear': 2020, 'format': 'json'}

    for store in data.itterrows():
        params['latitude'] = store['LAT']
        params['longitude'] = store['LONG']
        r = requests.get(url, params = params)
        try:
            j = json.loads(r.text)
            tracts.append(j['Block']['FIPS'][5:-4])
            counties.append(j['County']['name'])
        except:
            counties.append(np.nan)
            tracts.append(np.nan)

    data['COUNTY'] = counties
    data['TRACT'] = tracts

    return data

if __name__ == '__main__':
    google_addresses = get_store_addresses('co_cannabis_stores.csv')
    formatted_addresses = reformat_addresses(google_addresses)
    geocoded_addresses = geocode_coords(formatted_addresses)

    # export geocoded addresses as CSV
    geocoded_addresses.to_csv('geocoded_stores.csv', index = False)

