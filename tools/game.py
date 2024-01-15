from typing import List, Optional, Tuple, Dict, Any
import random
import time
from tools.card import CardContent
from tools.card_list import Deck, Hands
from tools.player import Player
from tools.logic import get_attack, get_attack_from_input
from tools.attack import Attack
from tools.utils import print_status


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

    def start(self) -> Optional[Dict[str, Any]]:
        human_player = self.get_human_player()
        deck = Deck(colors=self.colors, numbers=self.numbers)
        players = self.init_players(deck=deck, human_player=human_player)
        players_num = len(self.player_id_list)

        history = []
        opened_cards = []
        losers = 0
        attacker = self.start_attacker
        outputs = {"proba_list": [], "attack_results": []}
        for turn in range(1, self.max_turns + 1):
            print_status(players)
            player = players[attacker]
            print(f"Turn{turn} Attacker: {player.name}")
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
            strategies = [True, False]
            while True:
                maximize_entropy_strategy = strategies[player.player_id]
                attack, proba = self.act(human_player=human_player, player=player, opponents=opponents,
                                         new_card_content=new_card_content, has_succeeded=has_succeeded,
                                         opened_cards=opened_cards, history=history, maximize_entropy_strategy=maximize_entropy_strategy)

                if attack is None:
                    if not has_succeeded:
                        raise Exception(
                            "You can't skip your next attack because your attack has not succeeded yet.")
                    print("Skip the next attack.")
                    break

                print(f"Attack: {attack}")
                # Apply attack
                history.append(attack)
                outputs["proba_list"].append(proba)
                attacked_player = players[attack.attacked_to]
                print("Judging...")
                time.sleep(self.sleep_seconds)
                result = attacked_player.judge(attack=attack)
                outputs["attack_results"].append(result)
                if result:
                    print("Success!\n")
                    has_succeeded = True
                    opened_card: CardContent = attacked_player.open(
                        position=attack.position)
                    opened_cards.append(opened_card)
                    print_status(players=players)
                    # Judge whether the game is over or not
                    if attacked_player.is_loser():
                        losers += 1
                        if losers == players_num-1:
                            print(
                                f"The game is over! Winner: {player.name}")
                            outputs["history"] = history
                            outputs["winner"] = player.player_id
                            outputs["turns"] = turn
                            return outputs
                else:
                    print("Failed.")
                    if new_card is not None:
                        new_card = new_card.open()
                    break

            if new_card is not None:
                player.insert(new_card)
                print(f"Inserted: {new_card}")

            # switch attacker
            attacker = (attacker+1) % players_num
            print("\n")
        return

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
            opened_cards: List[CardContent], history: List[Attack], maximize_entropy_strategy: bool) -> Tuple[Optional[Attack], Optional[float]]:
        if (human_player is not None) and (player.player_id == human_player):
            attack = get_attack_from_input(
                player=player, opponents=opponents, new_card=new_card_content, has_succeeded=has_succeeded)
            proba = None
        else:
            print("Thinking...")
            time.sleep(self.sleep_seconds)
            attack, proba = get_attack(
                player=player,
                opponents=opponents,
                new_card=new_card_content,
                opened_cards=opened_cards,
                has_succeeded=has_succeeded,
                history=history,
                maximize_entropy_strategy=maximize_entropy_strategy
            )
        return attack, proba

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
