import os
import pandas as pd

start_path = os.path.join(os.path.dirname(__file__), f'Licensee List Archive')
for year in os.listdir(start_path):
    if '.DS_Store' in year:
        continue
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
                            print(f'got retail_df for {month_or_file} {year}')
                elif 'Store' in file or 'MED' in file:
                    sheet_path = os.path.join(month_path, file)
                    store_df = pd.read_excel(sheet_path)
                    print(f'got store_df for {month_or_file} {year}')
        else:
            month_df = pd.read_excel(month_path)
            print(f'got month_df for {month_or_file} {year}')
