import yfinance as yf
import pandas as pd
from ta import add_all_ta_features
from ta.utils import dropna
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

class Ticker:
    def __init__(self, ticker):
        self.ticker = ticker            # nom de la valeur boursiere, de la crypto, ...
        self.data = None                # les données récupérer de yfinance, avec les indicateurs tehcnique
        self.scaler = MinMaxScaler()    # les data scalées
        self.model = None               # le modèle utilisé pour les prédictions
        self.prediction = None;         # les données prédites avec le modèle

    def fetch_data(self, interval="1d", start="2017-01-01", end="2021-01-01"):
        self.data = yf.Ticker(self.ticker).history( interval=interval, start=start, end=end)
        if self.data.empty:
            raise ValueError(f"Aucune donnée disponible pour le ticker '{self.ticker}'")
        print("Données récupérées avec succès")

    def calculate_indicators(self):
        # Clean NaN values
        self.data.dropna(inplace=True)
        self.data = add_all_ta_features(self.data, 
                                        open="Open", high="High", low="Low", close="Close", volume="Volume_BTC", 
                                        fillna=True)
        self.data.dropna(inplace=True)
        print("Indicateurs calculés")

    def normalize_data(self):
        self.data[['Close', 'EMA']] = self.scaler.fit_transform(self.data[['Close', 'EMA']])
        print("Données normalisées")

    def save_data(self, filename="stock_data.csv"):
        self.data.to_csv(filename)
        print(f"Données enregistrées dans {filename}")

    def load_model_and_predict(self, model, window):
        predictions = model.predict(window)
        self.data['Predictions'] = predictions
        print("Prédictions réalisées")

    def display_data(self):
        self.data.head(5)

    def display_scaler(self):
        self.scaler.head(5)

    def visualize_predictions(self):
        plt.figure(figsize=(14,7))
        plt.plot(self.data['Close'], label='Valeur réelle')
        plt.plot(self.data['Predictions'], label='Prédictions')
        plt.legend()
        plt.show()
