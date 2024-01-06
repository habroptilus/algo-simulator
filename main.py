from tools.game import Game
from tools.consts import COLORS, NUMBERS, MAX_TURNS, START_ATTACKER, MAX_HANDS, PLAYER_ID_LIST


if __name__ == '__main__':
    game = Game(
        colors=COLORS, numbers=NUMBERS, max_turns=MAX_TURNS, start_attacker=START_ATTACKER,
        max_hands=MAX_HANDS, player_id_list=PLAYER_ID_LIST
    )
    game.start()
