import pandas as pd

# Chargement des données
df = pd.read_csv('DGS10.csv', parse_dates=['Date'])
df.sort_values('Date', inplace=True)

# Vérifiez le type de données et nettoyez la colonne YTM
df['YTM'] = pd.to_numeric(df['YTM'].str.strip(), errors='coerce')  # Convertit en numérique, remplace les erreurs par NaN
df = df.dropna(subset=['YTM'])  # Supprime les lignes où YTM est NaN

# Réinitialiser l'index pour s'assurer qu'il est continu
df.reset_index(drop=True, inplace=True)

# Resample les données pour obtenir les YTM mensuels
df.set_index('Date', inplace=True)
df_monthly = df.resample('ME').last().reset_index()  # Prendre la dernière valeur de chaque mois

# Ajouter une colonne pour la maturité restante en années
# Pour simplifier, supposons que la maturité est toujours de 10 ans
df_monthly['Maturity'] = 10  

# Convertir YTM en pourcentage (en tant que rendement annuel)
df_monthly['YTM'] = df_monthly['YTM'] / 100  # En pourcentage

# Ajouter une colonne pour le YTM mensuel
def calculate_monthly_yield(annual_yield):
    return (1 + annual_yield) ** (1/12) - 1  # Convertit YTM annuel en rendement mensuel

# Calculer le Monthly YTM
df_monthly['Monthly_YTM'] = df_monthly['YTM'].apply(calculate_monthly_yield)

# Calcul de la Duration Modifiée (Dt) et de la Convexité (Ct)
def calculate_duration_convexity(row):
    Yt = row['YTM']  # Utiliser le rendement annuel
    Mt = row['Maturity']
    
    # Duration modifiée : =(1-(1/(1+0,5*B3/100)^(2*10)))/(B3/100)
    Dt = (1 / Yt) * (1 - 1 / ((1 + 0.5 * Yt) ** (2 * Mt))) if Yt > 0 else None
    
    # Convexité : =(2/(B3/100)^2)*(1-(1/(1+B3/200)^(20)))-20/((B3/100)*(1+B3/200)^(21))
    Ct = (2 / (Yt ** 2)) * (1 - 1 / ((1 + 0.5 * Yt) ** (2 * Mt))) - (2 * Mt) / (Yt * (1 + 0.5 * Yt) ** (2 * Mt + 1)) if Yt > 0 else None
    
    return pd.Series([Dt, Ct])

df_monthly[['Duration', 'Convexity']] = df_monthly.apply(calculate_duration_convexity, axis=1)

# Calculer le retour sur investissement (Rt) sur la base des YTM des périodes mensuelles successives
def calculate_investment_return(current_row, previous_row):
    if previous_row is None:
        return None  # Pas de retour pour la première ligne
    
    Ymt_1 = previous_row['Monthly_YTM']
    Yt_1 = previous_row['YTM']  # Utiliser le YTM mensuel pour Yt-1
    Yt = current_row['YTM']      # Utiliser le YTM mensuel pour Yt
    Dt = current_row['Duration']
    Ct = current_row['Convexity']
    
    # Calcul du retour sur investissement : =-C4*(B4/100-B3/100)+0,5*D4*(B4/100-B3/100)^2+((1+B3/100)^(1/12)-1)
    return (Ymt_1 - Dt * (Yt - Yt_1) + 0.5 * Ct * (Yt - Yt_1) ** 2)

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
print(df_monthly[['Date', 'YTM', 'Monthly_YTM', 'Investment Return']])

# Enregistrer les résultats dans un fichier CSV
df_monthly.to_csv('bond_monthly_returns.csv', index=False)
print("Les résultats ont été enregistrés dans 'bond_monthly_returns.csv'")
