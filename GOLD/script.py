import pandas as pd
import matplotlib.pyplot as plt
import sys

# Define constants
CLOSE_COLUMN = 'Close'

# Define start date
start_date = pd.to_datetime(sys.argv[1]) if len(sys.argv) > 1 else pd.to_datetime('01-01-1961')

# Load the gold data
try:
    gold = pd.read_csv('xauusd_m.csv')
except FileNotFoundError:
    print("Le fichier 'xauusd_m.csv' est introuvable.")
    exit()

gold['Date'] = pd.to_datetime(gold['Date'])
gold.set_index('Date', inplace=True)

# Resample to monthly data and calculate monthly returns
gold_month = gold[gold.index.date >= start_date.date()].resample(rule="ME").first().ffill()[[CLOSE_COLUMN]]
gold_month['Monthly Change'] = gold_month[CLOSE_COLUMN].pct_change()
gold_month['Cumul Monthly Returns'] = (1 + gold_month['Monthly Change']).cumprod()

# Reset index to make 'Date' a column again for display
gold_month.reset_index(inplace=True)

# Format float values and print the result
pd.options.display.float_format = '{:.4f}'.format
print(gold_month[['Date', 'Monthly Change', 'Cumul Monthly Returns']])

# Save the results to CSV
gold_month[['Date', 'Monthly Change', 'Cumul Monthly Returns']].to_csv('gold_monthly_returns.csv', index=False, float_format='%.5f')
print("Les résultats ont été enregistrés dans 'gold_monthly_returns.csv'")

# Plotting the cumulative returns
plt.figure(figsize=(10, 5))
plt.plot(gold_month['Date'], gold_month['Cumul Monthly Returns'], label='Rendement Cumulé', color='gold')
plt.title('Rendement Cumulé de l\'Or')
plt.xlabel('Date')
plt.ylabel('Rendement Cumulé (%)')
plt.legend()
plt.grid()
plt.show()
