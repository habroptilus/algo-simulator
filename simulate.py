import argparse
from tools.game import Game
from tools.consts import COLORS, NUMBERS, MAX_TURNS, START_ATTACKER, MAX_HANDS, PLAYER_ID_LIST


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Algo Simulator Parser')

    parser.add_argument('--trials', '-t', type=int, default=10)

    args = parser.parse_args()
    winners = []
    proba_list = []
    attack_results = []
    different_between_strategies_list = []
    turns = []
    game = Game(
        colors=COLORS, numbers=NUMBERS, max_turns=MAX_TURNS, start_attacker=START_ATTACKER,
        max_hands=MAX_HANDS, player_id_list=PLAYER_ID_LIST, include_human_player=False, sleep_seconds=0)
    for _ in range(args.trials):
        outputs = game.start()
        proba_list += outputs["proba_list"]
        attack_results += outputs["attack_results"]
        different_between_strategies_list += outputs["different_between_strategies_list"]
        turns.append(outputs["turns"])
        winners.append(outputs["winner"])

    print(f"Win rate of Player1: {sum(winners)/len(winners)}")
    print(f"Calib: {sum(proba_list)/sum(attack_results)}")
    print(f"Avg turns: {sum(turns)/len(turns)}")
    print(
        f"Rate of difference between strategies: {sum(different_between_strategies_list)/len(different_between_strategies_list)}")
