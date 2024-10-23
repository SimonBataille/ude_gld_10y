import pandas as pd

# Define start date
start_date = pd.to_datetime('01-01-1961')

# Load the gold data
gold = pd.read_csv('xauusd_m.csv')
gold['Date'] = pd.to_datetime(gold['Date'])
gold.set_index('Date', inplace=True)

# Resample to monthly data and calculate monthly returns
gold_month = gold[gold.index.date >= start_date.date()].resample(rule="ME").first().ffill()[['Close']]
gold_month['Monthly Change'] = gold_month['Close'].pct_change()
gold_month['Cumul Monthly Returns'] = (1 + gold_month['Monthly Change']).cumprod()

# Reset index to make 'Date' a column again for display
gold_month.reset_index(inplace=True)

# Format float values and print the result
pd.options.display.float_format = '{:.4f}'.format
print(gold_month[['Date', 'Monthly Change', 'Cumul Monthly Returns']])

gold_month[['Date', 'Monthly Change', 'Cumul Monthly Returns']].to_csv('gold_monthly_returns.csv', index=False, float_format='%.5f')
print("Les résultats ont été enregistrés dans 'gold_monthly_returns.csv'")
