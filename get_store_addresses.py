import requests
import pandas as pd
import secrets
import json
import numpy as np

# initialize vars
url = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json'
key = secrets.google_key
p = {
    'inputtype': 'textquery',
    'key': key,
    'fields': 'name,formatted_address,geometry'
    }

i = 0

# read existing data
df = pd.read_csv('co_cannabis_stores.csv')

# initialize new var lists
lat_list = []
long_list = []
name_list = []
address_list = []

for store in df.iterrows():
    # grab store info
    if store[1][6] > 0:
        p['input'] = f'{store[1][2]} {int(store[1][6])}'
    else: # Oct 2017 data has no ZIP, so use city instead
        p['input'] = f'{store[1][2]} {store[1][5]}'

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
    if i % 500 == 0:
        print(f'finished {i} of {len(df)} records')
        print(f'{round(i / len(df) * 100, 2)}% done')

# save new columns
df['LAT'] = lat_list
df['LONG'] = long_list
df['google_name'] = name_list
df['address'] = address_list

# write to csv
df.to_csv('co_stores_addresses.csv')


