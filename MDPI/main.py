import pandas as pd
import numpy as np
from fredapi import Fred

# Remplacer 'your_api_key' par votre propre clé API FRED
FRED_API_KEY = 'your_api_key'

def fetch_ytm_data(start_date='1962-01-01'):
    """
    Récupérer les données YTM depuis la FRED
    """
    fred = Fred(api_key=FRED_API_KEY)
    ytm_data = fred.get_series('DGS10', observation_start=start_date)
    
    # Convertir en DataFrame pour faciliter les calculs
    df = pd.DataFrame(ytm_data, columns=['YTM'])
    df.index.name = 'Date'
    df.reset_index(inplace=True)

    # Garder uniquement les dernières observations de chaque mois
    df = df.resample('M', on='Date').last().dropna()

    return df

def modified_duration(ytm, maturity=10):
    """
    Calcul de la duration modifiée.
    """
    ytm = ytm / 100  # Convertir en fraction
    duration = (1 / ytm) * (1 - 1 / (1 + 0.5 * ytm)**(2 * maturity))
    return duration

def convexity(ytm, maturity=10):
    """
    Calcul de la convexité.
    """
    ytm = ytm / 100  # Convertir en fraction
    convexity = (2 / ytm**2) * (1 - 1 / (1 + 0.5 * ytm)**(2 * maturity)) - \
                (2 * maturity) / (ytm * (1 + 0.5 * ytm))**(2 * maturity + 1)
    return convexity

def bond_return(ytm_prev, ytm_curr, mod_duration, convexity):
    """
    Calcul du rendement d'une obligation entre deux périodes.
    """
    ytm_prev = ytm_prev / 100  # Convertir en fraction
    ytm_curr = ytm_curr / 100

    # Variation du YTM
    delta_ytm = ytm_curr - ytm_prev

    # Calcul du rendement
    return_total = ytm_prev - mod_duration * delta_ytm + 0.5 * convexity * delta_ytm**2
    return return_total * 100  # Retourner en pourcentage

def main():
    # Récupérer les données depuis la FRED
    df = fetch_ytm_data()

    # Calculer la duration modifiée et la convexité pour chaque période
    df['Modified_Duration'] = df['YTM'].apply(modified_duration)
    df['Convexity'] = df['YTM'].apply(convexity)

    # Calculer les rendements mensuels
    df['Return'] = df.apply(lambda row: bond_return(
        df['YTM'].shift(1)[row.name], row['YTM'], row['Modified_Duration'], row['Convexity']), axis=1)

    # Afficher les premiers résultats
    print(df.head())

    # Enregistrer les résultats dans un fichier CSV
    df.to_csv('bond_returns.csv', index=False)
    print("Les résultats ont été enregistrés dans 'bond_returns.csv'")

if __name__ == '__main__':
    main()
