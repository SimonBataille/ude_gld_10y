
import pandas as pd

# Charger les données et nettoyer
df = pd.read_csv('DGS10.csv', parse_dates=['Date']).dropna(subset=['YTM']).sort_values('Date').reset_index(drop=True)

# Convertir YTM en numérique et limiter à 4 décimales
df['YTM'] = pd.to_numeric(df['YTM'].str.strip(), errors='coerce').round(4) / 100  # Conversion en pourcentage

# Resample les données pour obtenir les YTM mensuels
df.set_index('Date', inplace=True)
df_monthly = df.resample('ME').last().reset_index()  # Prendre la dernière valeur de chaque mois

# Calcul de la Duration Modifiée (Dt) et de la Convexité (Ct)
def calculate_duration_convexity(Yt, Mt=10, epsilon=1e-6):
    if Yt <= epsilon:
        return pd.Series([None, None])
    
    # Calcul de la Duration modifiée
    Dt = (1 / Yt) * (1 - 1 / ((1 + 0.5 * Yt) ** (2 * Mt)))
    
    # Calcul de la Convexité
    Ct = (2 / (Yt ** 2)) * (1 - 1 / ((1 + 0.5 * Yt) ** (2 * Mt))) - (2 * Mt) / (Yt * (1 + 0.5 * Yt) ** (2 * Mt + 1))
    
    return pd.Series([Dt, Ct])

df_monthly[['Duration', 'Convexity']] = df_monthly['YTM'].apply(calculate_duration_convexity)

# Calculer les rendements mensuels et le retour sur investissement
df_monthly['Prev_YTM'] = df_monthly['YTM'].shift(1)
df_monthly['Monthly_Return'] = (1 + df_monthly['Prev_YTM']) ** (1 / 12) - 1
df_monthly['YTM_Diff'] = df_monthly['YTM'] - df_monthly['Prev_YTM']

# Calcul du retour sur investissement
df_monthly['Investment Return'] = df_monthly['Monthly_Return'] - df_monthly['Duration'] * df_monthly['YTM_Diff'] + 0.5 * df_monthly['Convexity'] * (df_monthly['YTM_Diff'] ** 2)

# Remplacer les valeurs NaN (notamment pour la première ligne) par 0
df_monthly['Investment Return'].fillna(0, inplace=True)

# Ajouter une colonne "Investment Return (%)" en pourcentage
df_monthly['Investment Return (%)'] = df_monthly['Investment Return'] * 100

# Calculer le produit cumulé
df_monthly['Cumul Monthly Returns']=(1+df_monthly['Investment Return']).cumprod()

# Afficher les résultats avec 4 décimales
pd.options.display.float_format = '{:.4f}'.format
print(df_monthly[['Date', 'YTM', 'Duration', 'Convexity', 'Investment Return', 'Investment Return (%)', 'Cumul Monthly Returns']])

# Exporter les résultats dans un fichier CSV
#df_monthly[['Date', 'YTM', 'Duration', 'Convexity', 'Investment Return']].to_csv('bond_monthly_returns.csv', index=False)
df_monthly[['Date', 'YTM', 'Duration', 'Convexity', 'Investment Return', 'Investment Return (%)', 'Cumul Monthly Returns']].to_csv('bond_monthly_returns.csv', index=False, float_format='%.5f')
print("Les résultats ont été enregistrés dans 'bond_monthly_returns.csv'")
