import argparse
from tools.game import Game
from tools.logic import EpsilonGreedy

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Algo Simulator Parser')

    parser.add_argument('--trials', '-t', type=int, default=10)

    args = parser.parse_args()
    winners = []
    proba_list = []
    attack_results = []
    different_between_strategies_list = []
    turns = []
    skip_counts = []

    logics = [EpsilonGreedy(epsilon=0),
              EpsilonGreedy(epsilon=1)]
    game = Game(logics=logics, sleep_seconds=0)

    for _ in range(args.trials):
        outputs = game.start()
        proba_list += outputs["proba_list"]
        attack_results += outputs["attack_results"]
        turns.append(outputs["turns"])
        winners.append(outputs["winner"])
        skip_counts.append(outputs["skip_count"])

    target_player = "CPU1"
    print(
        f"Win rate of {target_player}: {len([winner for winner in winners if winner == target_player])/len(winners)}")
    assert len(proba_list) == len(attack_results)
    print(f"Calib: {sum(proba_list)/sum(attack_results)}")
    print(f"Avg turns: {sum(turns)/len(turns)}")
    print(skip_counts)
