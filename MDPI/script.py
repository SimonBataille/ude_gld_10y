import pandas as pd

# Chargement des données
df = pd.read_csv('DGS10.csv', parse_dates=['Date'])
df.sort_values('Date', inplace=True)

# Vérifiez le type de données et nettoyez la colonne YTM
df['YTM'] = pd.to_numeric(df['YTM'].str.strip(), errors='coerce')  # Convertir en numérique, remplace les erreurs par NaN
df = df.dropna(subset=['YTM'])  # Supprimer les lignes où YTM est NaN

# Réinitialiser l'index pour s'assurer qu'il est continu
df.reset_index(drop=True, inplace=True)

# Resample les données pour obtenir les YTM mensuels
df.set_index('Date', inplace=True)
df_monthly = df.resample('ME').last().reset_index()  # Prendre la dernière valeur de chaque mois

# Convertir YTM en pourcentage (en tant que rendement annuel)
df_monthly['YTM'] = df_monthly['YTM'] / 100  # En pourcentage

# Calcul de la Duration Modifiée (Dt) et de la Convexité (Ct)
def calculate_duration_convexity(Yt, Mt=10):
    # Mt est fixé à 10 ans
    if Yt <= 0:
        return pd.Series([None, None])
    
    # Duration modifiée
    Dt = (1 / Yt) * (1 - 1 / ((1 + 0.5 * Yt) ** (2 * Mt)))
    
    # Convexité
    Ct = (2 / (Yt ** 2)) * (1 - 1 / ((1 + 0.5 * Yt) ** (2 * Mt))) - (2 * Mt) / (Yt * (1 + 0.5 * Yt) ** (2 * Mt + 1))
    
    return pd.Series([Dt, Ct])

# Appliquer les calculs de Duration et Convexité
df_monthly[['Duration', 'Convexity']] = df_monthly['YTM'].apply(calculate_duration_convexity)

# Calculer le retour sur investissement (Rt) sur la base des YTM des périodes mensuelles successives
def calculate_investment_return(current_row, previous_row):
    if previous_row is None:
        return None  # Pas de retour pour la première ligne
    
    Yt_1 = previous_row['YTM']  # YTM au début de la période (Yt-1)
    Yt = current_row['YTM']     # YTM actuel
    Dt = current_row['Duration']
    Ct = current_row['Convexity']
    
    # Calcul du rendement mensuel à partir du YTM annuel
    monthly_return = (1 + Yt_1) ** (1 / 12) - 1
    
    # Calcul du retour sur investissement
    return monthly_return - Dt * (Yt - Yt_1) + 0.5 * Ct * (Yt - Yt_1) ** 2

# Initialiser une liste pour stocker les retours
investment_returns = []

# Calculer les retours pour chaque ligne
for index, row in df_monthly.iterrows():
    if index == 0:
        investment_returns.append(None)  # Pas de retour pour la première ligne
    else:
        previous_row = df_monthly.iloc[index - 1]
        investment_return = calculate_investment_return(row, previous_row)
        investment_returns.append(investment_return)

# Ajouter les retours au DataFrame
df_monthly['Investment Return'] = investment_returns

# Affichage des résultats
print(df_monthly[['Date', 'YTM', 'Investment Return']])

# Enregistrer les résultats dans un fichier CSV
df_monthly.to_csv('bond_monthly_returns.csv', index=False)
print("Les résultats ont été enregistrés dans 'bond_monthly_returns.csv'")
