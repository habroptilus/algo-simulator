from typing import List, Optional
import random
import time
from tools.card import CardContent
from tools.card_list import Deck, Hands
from tools.player import Player
from tools.consts import PLAYERS_NUM
from tools.logic import get_attack, get_attack_from_input
from tools.attack import Attack


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


class Game:
    def __init__(self, colors: List[str], numbers: List[int], max_turns: int,
                 start_attacker: int,  max_hands: int, player_id_list: List[int],
                 include_human_player: bool, human_player: Optional[int] = None, sleep_seconds: int = 3):
        self.colors = colors
        self.numbers = numbers
        self.max_turns = max_turns
        self.start_attacker = start_attacker
        self.human_player: Optional[int] = human_player
        self.max_hands = max_hands
        self.player_id_list = player_id_list
        self.include_human_player = include_human_player
        self.sleep_seconds = sleep_seconds

    def start(self):
        human_player = self.get_human_player()
        deck = Deck(colors=self.colors, numbers=self.numbers)
        players = self.init_players(deck=deck, human_player=human_player)

        history = []
        opened_cards = []
        losers = 0
        attacker = self.start_attacker
        for turn in range(self.max_turns):
            print_status(players)
            player = players[attacker]
            print(f"Turn{turn+1} Attacker: {player.name}")
            opponents = [
                player for player in players if player.player_id != attacker]

            new_card = deck.draw(player_id=player.player_id)
            new_card_content: Optional[CardContent] = None
            if new_card is None:
                print("deck is empty.")
            else:
                new_card_content = new_card.get_content(
                    referred_by=player.player_id)

            has_succeeded = False
            while True:
                attack = self.act(human_player=human_player, player=player, opponents=opponents,
                                  new_card_content=new_card_content, has_succeeded=has_succeeded,
                                  opened_cards=opened_cards, history=history)

                if attack is None:
                    if not has_succeeded:
                        raise Exception(
                            "You can't skip your next attack because your attack has not succeeded yet.")
                    print("Skip the next attack.")
                    break

                print(f"Attack: {attack}")
                # Apply attack
                history.append(attack)
                opponent = players[attack.attacked_to]
                print("Judging...")
                time.sleep(self.sleep_seconds)
                result = opponent.hands.judge(attack=attack)
                if result:
                    print("Success!\n")
                    has_succeeded = True
                    opponent.hands = opponent.hands.open(
                        position=attack.position)
                    opened_cards.append(CardContent(
                        color=attack.card_content.color, number=attack.card_content.number))
                    print_status(players=players)
                    # Judge whether the game is over or not
                    if opponent.hands.is_loser():
                        losers += 1
                        if losers == PLAYERS_NUM-1:
                            print(
                                f"The game is over! Winner: {player.name}")
                            return player.player_id

                else:
                    print("Failed.")
                    if new_card is not None:
                        new_card.opened = True
                    break

            if new_card is not None:
                player.hands, _ = player.hands.insert(new_card)
                print(f"Inserted: {new_card}")

            # switch attacker
            attacker = (attacker+1) % PLAYERS_NUM
            print("\n")

    def get_human_player(self) -> Optional[int]:
        if self.include_human_player:
            human_player = self.human_player if self.human_player is not None else random.choice(
                self.player_id_list)
            print(f"You are Player{human_player}.")
        else:
            if self.human_player is not None:
                print(
                    "Warning: include_human_player is False but human_player is specified.")
            human_player = None
            print("Any Human player doesn't join this game.")
        return human_player

    def act(self, human_player: int, player: Player, opponents: List[Player],
            new_card_content: Optional[CardContent], has_succeeded: bool,
            opened_cards: List[CardContent], history: List[Attack]) -> Optional[Attack]:
        if (human_player is not None) and (player.player_id == human_player):
            attack = get_attack_from_input(
                player=player, opponents=opponents, new_card=new_card_content, has_succeeded=has_succeeded)
        else:
            print("Thinking...")
            time.sleep(self.sleep_seconds)
            attack = get_attack(
                player=player,
                opponents=opponents,
                new_card=new_card_content,
                opened_cards=opened_cards,
                has_succeeded=has_succeeded,
                history=history,
            )
        return attack

    def init_player(self, deck: Deck, player_id: int, name: str) -> Player:
        hands = Hands(cards=[deck.draw(player_id=player_id)
                             for _ in range(self.max_hands)])
        return Player(player_id=player_id, hands=hands, name=name)

    def init_players(self, deck: Deck, human_player: Optional[int]) -> List[Player]:
        players: List[Player] = []
        cpu_num = 1
        for player_id in self.player_id_list:
            if (human_player is not None) and (player_id == human_player):
                name = "You "
            else:
                name = f"CPU{cpu_num}"
                cpu_num += 1
            player = self.init_player(
                deck=deck, player_id=player_id, name=name)
            players.append(player)
        return players
