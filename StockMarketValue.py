import yfinance as yf
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

class StockMarketValue:
    def __init__(self, ticker):
        self.ticker = ticker
        self.data = None
        self.scaler = MinMaxScaler()

    def fetch_data(self, start="2017-01-01", end="2021-01-01"):
        self.data = yf.Ticker(self.ticker).history(start=start, end=end)
        if self.data.empty:
            raise ValueError(f"Aucune donnée disponible pour le ticker '{self.ticker}'")
        print("Données récupérées avec succès")

    def calculate_indicators(self):
        self.data['EMA'] = self.data['Close'].ewm(span=20, adjust=False).mean()
        self.data.dropna(inplace=True)
        print("Indicateurs calculés")

    def normalize_data(self):
        self.data[['Close', 'EMA']] = self.scaler.fit_transform(self.data[['Close', 'EMA']])
        print("Données normalisées")

    def save_data(self, filename="stock_data.csv"):
        self.data.to_csv(filename)
        print(f"Données enregistrées dans {filename}")

    def load_model_and_predict(self, model):
        predictions = model.predict(self.data[['Close', 'EMA']].values)
        self.data['Predictions'] = predictions
        print("Prédictions réalisées")

    def visualize_predictions(self):
        plt.figure(figsize=(14,7))
        plt.plot(self.data['Close'], label='Valeur réelle')
        plt.plot(self.data['Predictions'], label='Prédictions')
        plt.legend()
        plt.show()
