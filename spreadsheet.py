import os
import re
import pandas as pd
from datetime import datetime
import gspread 
import time 
import os
# env variables
gc = gspread.service_account(filename=os.environ['CREDENTIALS_PATH'])

df = pd.read_pickle('data/merged.pkl')

df['Total Amount'] = df['Total Amount'].abs()

def get_positions(month_number):
    column_letters = ['A', 'D', 'G', 'J', 'M', 'P']
    base_row = 18 if month_number <= 6 else 63
    return {
        'expenses': f'{column_letters[(month_number - 1) % 6]}{base_row}',
        'savings': f'{column_letters[(month_number - 1) % 6]}{base_row + 20}',
        'income': f'{column_letters[(month_number - 1) % 6]}{base_row + 35}',
    }

pos = {month: get_positions(i+1) for i, month in enumerate(['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'])}
start_year = 2019
current_year = datetime.now().year
years = [str(i) for i in range(start_year, current_year + 1)]

def get_year(year):
    year_df = df[df['M/Y'].str.contains(year)]
    return year_df

def get_month(year_df, month):
    # convert month to 2 digit format
    month = str(datetime.strptime(month, '%B').strftime('%m'))
    # must contain month/ 
    month_df = year_df[year_df['M/Y'].str.contains(month + '/')]
    return month_df

# print(get_month(get_year('2020'), 'April'))

def update_spreadsheet(gc, years, pos):
    for i in range(len(years)):
        year = years[i]
        year_df = get_year(year)

        wks = gc.open("Expenses").worksheet(year)
        for month in pos:
            month_df = get_month(year_df, month)

            if month_df.empty:
                continue

            income = month_df[month_df['Category'] == 'Income'][['Category', 'Total Amount']]
            savings = month_df[month_df['Category'].isin(['Savings', 'Trading'])][['Category', 'Total Amount']]
            expenses = month_df[~month_df['Category'].isin(['Income', 'Savings', 'Trading'])][['Category', 'Total Amount']]

            wks.update(pos[month]['expenses'], expenses.values.tolist())
            wks.update(pos[month]['income'], income.values.tolist())
            wks.update(pos[month]['savings'], savings.values.tolist())

            time.sleep(10)


# prediction for 100,000 pound
        
update_spreadsheet(gc, years, pos)