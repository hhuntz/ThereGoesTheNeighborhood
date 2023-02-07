import os
import pandas as pd

start_path = os.path.join(os.path.dirname(__file__), f'Licensee List Archive')
for year in os.listdir(start_path):
    if '.DS_Store' in year:
            continue
    if int(year) > 2013: # skip early years b/c formats vary and not relevant
        year_path = os.path.join(start_path, year)
        for month_or_file in os.listdir(year_path):
            if '.DS_Store' in month_or_file:
                continue
            month_path = os.path.join(year_path, month_or_file)
            if os.path.isdir(month_path):
                for file in os.listdir(month_path):
                    if 'Retail' in file:
                        retail_path = os.path.join(month_path, file)
                        for sheet in os.listdir(retail_path):
                            if 'Store' in sheet:
                                sheet_path = os.path.join(retail_path, sheet)
                                retail_df = pd.read_excel(sheet_path)
                                #print(f'got retail_df for {month_or_file} {year}')
                    elif 'Store' in file or 'MED' in file:
                        sheet_path = os.path.join(month_path, file)
                        store_df = pd.read_excel(sheet_path)
                        #print(f'got store_df for {month_or_file} {year}')
            else:
                # load data
                month_df = pd.read_excel(month_path, header = 1, dtype = object)
                # standardize formatting
                month_df = month_df.rename(columns=lambda x: x.strip().upper()) # strip whitespace from col names
                if 'LICENSE TYPE' in month_df.columns:
                    month_df['TYPE'] = month_df['LICENSE TYPE']
                # add date column
                try:
                    date = month_or_file.split('.')[0].split()[-1]
                    if date not in ['SAR', '443P']:
                        month_df['DATE'] = date
                    else:
                        month_df['DATE'] = month_or_file.split('.')[0].split()[-2]
                except: # error means no type field, either from before rec legaliation or data source error
                    continue
                # add rows to final df
                