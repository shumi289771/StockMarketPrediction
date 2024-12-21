import json
import logging
import websocket
import time

# Configuration des logs
logging.basicConfig(
    filename="real_test_log.log",
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

# API MyBetting
API_URL = "wss://api.mybettingapi.com/websocket"  # URL WebSocket de MyBettingAPI
AUTH_TOKEN = "VOTRE_TOKEN_ICI"  # Remplacez par votre clé API

# Calculer le montant du pari
def calculate_bet_amount():
    return max(BANKROLL * BET_PERCENTAGE, MIN_BET)

# Placer un pari
def place_bet(match_id, amount):
    """
    Placer un pari via l'API.
    """
    logger.info(f"Placement d'un pari sur le match {match_id} pour {amount:.2f} €")
    # Simuler un appel API pour placer le pari
    # Dans un vrai scénario, utilisez requests ou websocket pour envoyer une requête
    # Ex. : websocket.send(json.dumps({"action": "place_bet", "match_id": match_id, "amount": amount}))
    pass

# Gestion des messages WebSocket
def on_message(ws, message):
    global BANKROLL

    # Décoder le message
    data = json.loads(message)

    # Vérifier si c'est un match en direct
    if "match" in data:
        match = data["match"]
        match_id = match["id"]
        time_played = match["time"]
        score_home = match["score_home"]
        score_away = match["score_away"]
        draw_odds = match["odds"]["draw"]

        # Critères de la stratégie
        if (
            time_played >= 80
            and score_home == score_away
            and draw_odds > 1.2
        ):
            bet_amount = calculate_bet_amount()
            if BANKROLL >= bet_amount:
                # Placer un pari
                place_bet(match_id, bet_amount)

                # Simuler un résultat (50 % de chances de gagner pour tester)
                result = "win" if time.time() % 2 == 0 else "loss"
                if result == "win":
                    BANKROLL += bet_amount * (draw_odds - 1)
                    logger.info(f"PARI GAGNÉ - Match ID: {match_id}, Bankroll: {BANKROLL:.2f} €")
                else:
                    BANKROLL -= bet_amount
                    logger.info(f"PARI PERDU - Match ID: {match_id}, Bankroll: {BANKROLL:.2f} €")

            else:
                logger.warning(f"Bankroll insuffisant pour parier sur le match {match_id}")

# Gestion des erreurs
def on_error(ws, error):
    logger.error(f"Erreur WebSocket : {error}")

# Fermeture de la connexion
def on_close(ws, close_status_code, close_msg):
    logger.info("Connexion WebSocket fermée.")

# Connexion WebSocket
def on_open(ws):
    logger.info("Connexion WebSocket ouverte.")
    # Authentification
    auth_message = json.dumps({"action": "authenticate", "token": AUTH_TOKEN})
    ws.send(auth_message)

    # S'abonner aux matchs en direct
    subscribe_message = json.dumps({"action": "subscribe", "market": "live"})
    ws.send(subscribe_message)

# Lancer le WebSocket
def start_websocket():
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        API_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    ws.run_forever()

if __name__ == "__main__":
    start_websocket()
