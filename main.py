import argparse
from tools.game import Game
from tools.consts import COLORS, NUMBERS, MAX_TURNS, START_ATTACKER, MAX_HANDS, PLAYER_ID_LIST


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Algo Simulator Parser')

    parser.add_argument('--human-player', '-hp', type=int)
    parser.add_argument('--no-human', action='store_true')

    args = parser.parse_args()

    include_human_player = not args.no_human

    game = Game(
        colors=COLORS, numbers=NUMBERS, max_turns=MAX_TURNS, start_attacker=START_ATTACKER,
        max_hands=MAX_HANDS, player_id_list=PLAYER_ID_LIST, include_human_player=include_human_player,
        human_player=args.human_player)
    game.start()
