import json
import logging
import requests
import websocket
import time

# Configuration des logs
logging.basicConfig(
    filename="smarkets_strategy.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

# Bankroll initial
INITIAL_BANKROLL = 100.0
BANKROLL = INITIAL_BANKROLL

# Paramètres de stratégie
BET_PERCENTAGE = 0.02  # Pourcentage du bankroll par pari (2 %)
MIN_BET = 2.0  # Montant minimum pour chaque pari

# Configuration Smarkets API
SMARKETS_API_URL = "https://api.smarkets.com/v3/"
LOGIN_URL = SMARKETS_API_URL + "sessions/"
WEB_SOCKET_URL = "wss://api.smarkets.com/v3/subscriptions/"
USERNAME = "votre_email@example.com"
PASSWORD = "votre_mot_de_passe"

# Variables globales
SESSION_TOKEN = None


# Authentification
def authenticate():
    global SESSION_TOKEN
    response = requests.post(
        LOGIN_URL,
        json={"username": USERNAME, "password": PASSWORD}
    )
    if response.status_code == 200:
        SESSION_TOKEN = response.cookies.get("session")
        logger.info("Authentification réussie.")
    else:
        logger.error(f"Erreur lors de l'authentification : {response.status_code}")
        raise Exception("Échec de l'authentification")


# Calculer le montant du pari
def calculate_bet_amount():
    return max(BANKROLL * BET_PERCENTAGE, MIN_BET)


# Placer un pari
def place_bet(contract_id, amount):
    """
    Placer un pari via Smarkets API.
    """
    if SESSION_TOKEN is None:
        authenticate()

    headers = {"Authorization": f"Bearer {SESSION_TOKEN}"}
    payload = {
        "contract_id": contract_id,
        "price": 1.2,  # Cote minimale pour le nul
        "quantity": amount,
        "side": "buy"  # Acheter le pari sur le nul
    }
    response = requests.post(
        SMARKETS_API_URL + "orders/",
        json=payload,
        headers=headers
    )

    if response.status_code == 201:
        logger.info(f"Pari placé avec succès sur le contrat {contract_id} pour {amount:.2f} €")
    else:
        logger.error(f"Erreur lors du placement du pari : {response.json()}")


# Gestion des messages WebSocket
def on_message(ws, message):
    global BANKROLL

    data = json.loads(message)
    events = data.get("events", [])

    for event in events:
        if event["type"] == "quote":
            market = event["market"]
            contract = market["contract"]
            time_played = market["time_elapsed"]
            draw_odds = market["odds"]["draw"]

            # Vérification des critères de la stratégie
            if (
                time_played >= 80
                and draw_odds > 1.2
                and contract["score"]["home"] == contract["score"]["away"]
            ):
                bet_amount = calculate_bet_amount()
                if BANKROLL >= bet_amount:
                    place_bet(contract["id"], bet_amount)

                    # Simuler un résultat (50 % de chances de gagner pour tester)
                    result = "win" if time.time() % 2 == 0 else "loss"
                    if result == "win":
                        BANKROLL += bet_amount * (draw_odds - 1)
                        logger.info(f"PARI GAGNÉ - Contrat ID: {contract['id']}, Bankroll: {BANKROLL:.2f} €")
                    else:
                        BANKROLL -= bet_amount
                        logger.info(f"PARI PERDU - Contrat ID: {contract['id']}, Bankroll: {BANKROLL:.2f} €")
                else:
                    logger.warning(f"Bankroll insuffisant pour parier sur le contrat {contract['id']}")


# Gestion des erreurs
def on_error(ws, error):
    logger.error(f"Erreur WebSocket : {error}")


# Fermeture de la connexion
def on_close(ws, close_status_code, close_msg):
    logger.info("Connexion WebSocket fermée.")


# Connexion WebSocket
def on_open(ws):
    logger.info("Connexion WebSocket ouverte.")
    # Exemple de message pour s'abonner aux marchés
    subscription_message = {
        "action": "subscribe",
        "channels": ["market_quotes"]
    }
    ws.send(json.dumps(subscription_message))


# Lancer le WebSocket
def start_websocket():
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        WEB_SOCKET_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    ws.run_forever()


if __name__ == "__main__":
    authenticate()
    start_websocket()
