'''
This is one file to combine all of the programmatic data wrangling steps.

Before this, dispensary license records were manually combined here:
    https://docs.google.com/spreadsheets/d/1i2ASwYq7ZfX76pll3Sxc0Jw9yYac8svfa6LnSfxOLLY/edit?usp=sharing
They came from CO public records here:
    https://drive.google.com/drive/folders/0B-ZjnNx-rL_mTHU4dHhiX1dEbU0?resourcekey=0-j0x5DFB5M-7nNRLa-8g2Zw

The hand-aggregated records were saved as CO Cannabis Shops.xlsx, which is in the repo

The steps below take that data and:
    1. Filter the data and manage missing values
    2. Transform to individual dispensary records
    3. Use the Google Maps API (key req'd) to get formal addresses for each dispensary
    4. Use the US Census Bureau API to get gov't info (tract num, county, etc.) for each dispensary
    5. Output the final dispensary-level data for analysis
    6. Transform to tract-level records
    7. Out the final tract-level data for analysis
'''

import pandas as pd
import numpy as np
import os
import requests
import json
import math
import secrets_ # .py file with GoogleMaps API Key


def initial_wrangling(filename):
    df = pd.read_excel(filename, sheet_name = None)
    # combine to one df
    df = pd.concat(df.values(), ignore_index=True)
    # keep only med and rec store licenses -- remove grows, manufacturers, etc.
    df_stores = df[df['NUM'].str.contains('402R-|402-', na = False, regex = True)]
    # change TYPE vals
    # some missing in data; rest unclear
    df_stores['TYPE'] = np.where(df_stores['NUM'].str.contains('402R-'), 'Rec', 'Med')
    # fill missing DBA names with LLC names
    df_stores.DBA = df_stores.DBA.fillna(df.NAME)
    # remove 'LLC' from DBA names
    df_stores.DBA = df_stores.DBA.str.replace(' LLC', '')

    return df_stores

def get_disp_level(df_stores):
    # grab first and last months and years aggregated at dispensary level
    aggregation_functions = {'TYPE': lambda x: ', '.join(x.unique()), 'CITY': 'first', 
                            'YEAR': ['first', 'last'], 'MONTH': ['first', 'last']}
    # groupby name and zip -- some (112) names have multiple zips 
    df_new = df_stores.groupby([df_stores['DBA'], df_stores['ZIP']]).aggregate(aggregation_functions)
    # rename columns and take a look
    df_new.columns = ['TYPE', 'CITY', 'YEAR_FIRST', 'YEAR_LAST', 'MONTH_FIRST', 'MONTH_LAST']

    return df_new
    
def get_store_addresses(df):
    '''
    queries Google Maps API for street addresses based on location search
    requires local 'secrets_.py' file with API key
    returns dataframe same as input file w/ additional columns
    '''

    # initialize vars
    url = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json'
    key = secrets_.google_key
    p = {
        'inputtype': 'textquery',
        'key': key,
        'fields': 'name,formatted_address,geometry',
        'locationbias': 'circle:645000@39.5501,105.7821' # bias for results in Colorado
        }

    i = 0 # counter to track progress

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
    could use this or 'geocode_coords' function; 
        coordinates will give a match for each query, 
        but using addresses allows for more troubleshooting
    '''
    i = 0 # counter to track progress

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
    '''
    uses FCC API to get county and census tract from lat/long
    more useful than geocode_addresses, but only if you're sure the input coords are good
    returns input dataframe with new columns for each record
    '''

    # initialize vars
    i = 0 # counter to track progress
    counties = []
    tracts = []
    url = 'https://geo.fcc.gov/api/census/block/find'
    params = {'censusYear': 2020, 'format': 'json'}

    # make request for each store
    for store in data.iterrows():
        params['latitude'] = store[1][9] # get lat
        params['longitude'] = store[1][10] # get long
        r = requests.get(url, params = params)
        try: # parse JSON response
            j = json.loads(r.text)
            tracts.append(j['Block']['FIPS'][5:-4])
            counties.append(j['County']['name'])
        except:
            # if no response, add NAN vals
            counties.append(np.nan)
            tracts.append(np.nan)

                # track progress
        i += 1
        if i % 20 == 0:
            print(f'finished geocoding {i} of {len(data)} addresses')
            print(f'{round(i / len(data) * 100, 2)}% done')

    data['COUNTY'] = counties
    data['TRACT'] = tracts

    return data

def get_store_months(df):
    tract_dict = {}

    for row in df.iterrows():
        if not math.isnan(row[1][14]):
            start_year = row[1][5]
            start_month = row[1][7]
            end_year = row[1][6]
            end_month = row[1][8]
            tract = int(row[1][14])

            if tract not in tract_dict:
                tract_dict[tract] = {}

            years = range(start_year, end_year)
            for year in years:
                if 'Med' in row[1][3]:
                    if year == years[0]:
                        new_months = 12 - start_month
                    elif year == years[-1]:
                        new_months = end_month
                    else:
                        new_months = 12
                    tract_dict[tract][str(year) + '_med'] = tract_dict[tract].get(str(year) + '_med', 0) + new_months
                if 'Rec' in row[1][3]:
                    if year == years[0]:
                        new_months = 12 - start_month
                    elif year == years[-1]:
                        new_months = end_month
                    else:
                        new_months = 12
                    tract_dict[tract][str(year) + '_rec'] = tract_dict[tract].get(str(year) + '_rec', 0) + new_months
                    
    new_df = pd.DataFrame.from_dict(tract_dict, orient='index')
    med_df = new_df.filter([col for col in new_df.columns if 'med' in col])
    rec_df = new_df.filter([col for col in new_df.columns if 'rec' in col])
    
    med_df = med_df.cumsum(axis = 1)
    rec_df = rec_df.cumsum(axis = 1)
    
    rec_df.columns = [str(year) + '_rec' for year in range(2014, 2022)]
    med_df.columns = [str(year) + '_med' for year in range(2014, 2022)]
    both_df = med_df.merge(rec_df, right_index = True, left_index = True)
    both_df['total'] = rec_df.max(axis = 1) + med_df.max(axis = 1)
    
    return both_df

if __name__ == '__main__':
    # 1. Filter the data and manage missing values
    wrangled_stores = initial_wrangling('CO Cannabis Shops.xlsx')

    # 2. Transform to individual dispensary records
    disp_level = get_disp_level(wrangled_stores)

    # 3. Use the Google Maps API (key req'd) to get formal addresses for each dispensary
    google_addresses = get_store_addresses(disp_level)

    # 4. Use the US Census Bureau API to get gov't info (tract num, county, etc.) for each dispensary

    # could use addresses instead of lat/long coords to geotag
    #formatted_addresses = reformat_addresses(google_addresses)
    #geocoded_addresses = geocode_addresses(formatted_addresses)

    # use either above 2 lines or below 1
    geocoded_addresses = geocode_coords(google_addresses)

    # 5. Output the final dispensary-level data for analysis
    geocoded_addresses.to_csv('geocoded_stores_v2.csv', index = False)
        
    # 6. Transform to tract-level records
    tract_level = get_store_months(geocoded_addresses)

    # 7. Out the final tract-level data for analysis
    tract_level.to_csv('tract_records.csv')