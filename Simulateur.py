import random
import logging

# Configuration des logs
logging.basicConfig(
    filename="simulation_log.log",  # Fichier de log
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
WIN_MULTIPLIER = 1.5  # Multiplicateur en cas de gain (ex : cote 1.5)

# Simuler des matchs
def generate_match_data(num_matches=100):
    """
    Génère des données simulées de matchs.
    :param num_matches: Nombre de matchs simulés.
    :return: Liste de matchs.
    """
    matches = []
    for _ in range(num_matches):
        match = {
            "id": random.randint(1000, 9999),
            "time": random.randint(70, 90),  # Temps du match (70 à 90 minutes)
            "score_home": random.randint(0, 3),
            "score_away": random.randint(0, 3),
            "draw_odds": round(random.uniform(1.1, 3.0), 2),  # Cote pour le nul
        }
        matches.append(match)
    return matches

# Calculer le montant du pari
def calculate_bet_amount():
    """
    Calcule le montant du pari en fonction du bankroll.
    :return: Montant du pari.
    """
    return max(BANKROLL * BET_PERCENTAGE, MIN_BET)

# Appliquer la stratégie
def simulate_strategy(matches):
    """
    Simule la stratégie sur une liste de matchs.
    :param matches: Liste de matchs simulés.
    :return: Résultats de la simulation.
    """
    global BANKROLL
    total_bets = 0
    wins = 0
    losses = 0

    for match in matches:
        # Appliquer les critères
        if (
            match["time"] >= 80
            and match["score_home"] == match["score_away"]
            and match["draw_odds"] > 1.2
        ):
            bet_amount = calculate_bet_amount()
            if BANKROLL < bet_amount:
                logger.warning("Bankroll insuffisant pour placer un pari.")
                continue

            # Simuler un résultat (50 % de chances de gagner)
            result = random.choice(["win", "loss"])

            if result == "win":
                BANKROLL += bet_amount * (WIN_MULTIPLIER - 1)  # Ajouter les gains
                wins += 1
            else:
                BANKROLL -= bet_amount  # Déduire les pertes
                losses += 1

            total_bets += 1
            logger.info(
                f"Pari placé sur Match ID {match['id']} : {result.upper()} - "
                f"Montant : {bet_amount:.2f} €, Bankroll : {BANKROLL:.2f} €"
            )

    # Résumé des résultats
    return {
        "total_bets": total_bets,
        "wins": wins,
        "losses": losses,
        "final_bankroll": BANKROLL,
        "roi": (BANKROLL - INITIAL_BANKROLL) / INITIAL_BANKROLL * 100,
    }

# Lancer la simulation
def main():
    logger.info("Début de la simulation...")
    matches = generate_match_data(num_matches=100)  # Générer 100 matchs simulés
    results = simulate_strategy(matches)

    # Résumé final
    logger.info("Simulation terminée.")
    logger.info(f"Total des paris : {results['total_bets']}")
    logger.info(f"Paris gagnés : {results['wins']}")
    logger.info(f"Paris perdus : {results['losses']}")
    logger.info(f"Bankroll final : {results['final_bankroll']:.2f} €")
    logger.info(f"ROI : {results['roi']:.2f} %")

    print("=== Résultats de la simulation ===")
    print(f"Total des paris : {results['total_bets']}")
    print(f"Paris gagnés : {results['wins']}")
    print(f"Paris perdus : {results['losses']}")
    print(f"Bankroll final : {results['final_bankroll']:.2f} €")
    print(f"ROI : {results['roi']:.2f} %")

if __name__ == "__main__":
    main()
