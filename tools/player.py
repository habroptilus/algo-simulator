from typing import Optional
from tools.card_list import Hands
from tools.card import Card


class Player:
    def __init__(self, player_id: int, hands: Hands, name: Optional[str] = None):
        self.player_id = player_id
        self.hands = hands
        self.name = name if name is not None else "Player{player_id}"

    def __repr__(self) -> str:
        return f"{self.name}: {self.hands}"

    def debug(self) -> str:
        return f"{self.name}: {self.hands.debug()}"

    def insert(self, card: Card) -> 'Player':
        card = card.belongs_to(self.player_id)
        hands = self.hands.insert(card=card)
        return Player(player_id=self.player_id, hands=hands, name=self.name)
