from typing import List
from tools.player import Player


def print_status(players: List[Player]) -> None:
    player_name_len = max([len(player.name) for player in players])
    player_hands_len = max([len(player.hands) for player in players])
    header = " "*(player_name_len+2) + \
        " ".join([f"{str(i).rjust(3, ' ')}" for i in range(player_hands_len)])
    title = "State"
    upper_parts = "="*int((len(header)-len(title))/2)
    print(upper_parts + title + upper_parts)
    print(header)
    for player in players:
        print(player)
    print("="*len(header))
