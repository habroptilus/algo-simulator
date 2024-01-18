from typing import Optional, Any
import time
from tools.card import CardContent
from tools.card_list import Deck, Hands
from tools.player import Player
from tools.logic import LogicBase
from tools.utils import print_status
from tools.consts import COLORS, NUMBERS, MAX_HANDS, MAX_TURNS, SLEEP_SECONDS


class Game:
    def __init__(self, logics: list[LogicBase], colors: list[str] = COLORS,
                 numbers: list[int] = NUMBERS, max_turns: int = MAX_TURNS,
                 max_hands: int = MAX_HANDS,
                 sleep_seconds: int = SLEEP_SECONDS):
        self.logics = logics
        self.colors = colors
        self.numbers = numbers
        self.max_turns = max_turns
        self.max_hands = max_hands
        self.sleep_seconds = sleep_seconds

    def start(self) -> Optional[dict[str, Any]]:
        history = []
        opened_cards = []
        losers = 0
        attacker_id = 0

        deck = Deck(colors=self.colors, numbers=self.numbers)
        players = self.init_players(deck=deck)

        outputs = {"proba_list": [],
                   "attack_results": [], "skip_count": [0, 0]}

        for turn in range(1, self.max_turns + 1):
            print_status(players)
            attacker = players[attacker_id]
            print(f"Turn{turn} Attacker: {attacker.name}")
            opponents = [
                player for player in players if player.player_id != attacker.player_id]

            new_card = deck.draw(player_id=attacker.player_id)
            new_card_content: Optional[CardContent] = None
            if new_card is None:
                print("deck is empty.")
            else:
                new_card_content = new_card.get_content(
                    referred_by=attacker.player_id)

            has_succeeded = False

            while True:
                logic = self.logics[attacker_id]
                attack, meta = logic.act(player=attacker, opponents=opponents,
                                         new_card=new_card_content, has_succeeded=has_succeeded,
                                         opened_cards=opened_cards, history=history)

                if attack is None:
                    if not has_succeeded:
                        raise Exception(
                            "You can't skip your next attack because your attack has not succeeded yet.")
                    print("Skip the next attack.")
                    outputs["skip_count"][attacker.player_id] += 1
                    break

                print(f"Attack: {attack}")
                # Apply attack
                history.append(attack)
                outputs["proba_list"].append(meta.get("proba"))
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
                        if losers == len(self.logics)-1:
                            print(
                                f"The game is over! Winner: {attacker.name}")
                            outputs["history"] = history
                            outputs["winner"] = attacker.player_id
                            outputs["turns"] = turn
                            return outputs
                else:
                    print("Failed.")
                    if new_card is not None:
                        new_card = new_card.open()
                    break

            if new_card is not None:
                attacker.insert(new_card)
                print(f"Inserted: {new_card}")

            # switch attacker
            attacker_id = self.get_next_attacker(attacker_id)
            print("\n")
        return

    def get_next_attacker(self, attacker_id) -> int:
        return (attacker_id+1) % len(self.logics)

    def init_player(self, deck: Deck, player_id: int, name: str) -> Player:
        hands = Hands(cards=[deck.draw(player_id=player_id)
                             for _ in range(self.max_hands)])
        return Player(player_id=player_id, hands=hands, name=name)

    def init_players(self, deck: Deck) -> list[Player]:
        players: list[Player] = []
        cpu_num = 1
        for player_id in range(len(self.logics)):
            name = f"CPU{cpu_num}"
            cpu_num += 1
            player = self.init_player(
                deck=deck, player_id=player_id, name=name)
            players.append(player)
        return players
