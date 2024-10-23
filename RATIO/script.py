import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Chargement des données avec gestion des exceptions
try:
    gold_data = pd.read_csv('gold_monthly_returns.csv')
    bonds_data = pd.read_csv('bonds_monthly_returns.csv')
except FileNotFoundError as e:
    print(f"Erreur de fichier : {e}")
    exit()

# Conversion des dates en datetime
gold_data['Date'] = pd.to_datetime(gold_data['Date'])
bonds_data['Date'] = pd.to_datetime(bonds_data['Date'])

# Validation des données
assert not gold_data.duplicated('Date').any(), "Duplicated dates in gold data"
assert not bonds_data.duplicated('Date').any(), "Duplicated dates in bonds data"

# Fusion des deux DataFrames sur la date
merged_data = pd.merge(gold_data, bonds_data, on='Date', suffixes=('_Gold', '_Bonds'))

# Debug
# ~ import pdb; pdb.set_trace()

# Remplacer les NaN par 1 (ou utiliser ffill)
merged_data['Cumul Monthly Returns_Gold'] = merged_data['Cumul Monthly Returns_Gold'].ffill().fillna(1)
merged_data['Cumul Monthly Returns_Bonds'] = merged_data['Cumul Monthly Returns_Bonds'].ffill().fillna(1)


# Calcul du ratio des rendements cumulés
merged_data['Cumul Ratio'] = (merged_data['Cumul Monthly Returns_Gold'] / 
                               merged_data['Cumul Monthly Returns_Bonds']) * 100

# Ajustement des valeurs pour base 100
merged_data['Cumul Ratio'] = (merged_data['Cumul Ratio'] / merged_data['Cumul Ratio'].iloc[0]) * 100

# Calcul de la moyenne mobile à 7 ans (84 mois)
merged_data['Cumul Ratio MA'] = merged_data['Cumul Ratio'].rolling(window=84).mean()

# Affichage des résultats
print(merged_data[['Date', 'Cumul Ratio', 'Cumul Ratio MA']])

# Tracer le ratio sur une échelle logarithmique
plt.figure(figsize=(12, 6))
plt.plot(merged_data['Date'], merged_data['Cumul Ratio'], marker='o', label='Cumul Ratio')
plt.plot(merged_data['Date'], merged_data['Cumul Ratio MA'], color='orange', label='Moyenne Mobile (7 ans)')
plt.yscale('log')
plt.title('Ratio Cumulé de l\'Or sur les Obligations (Base 100) avec Moyenne Mobile à 7 ans')
plt.xlabel('Date')
plt.ylabel('Ratio Cumulé (Log Scale)')
plt.legend()
plt.grid()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Sauvegarde des résultats
# ~ merged_data.to_csv('merged_data_results.csv', index=False)
