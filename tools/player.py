from typing import Optional
from tools.card_list import Hands
from tools.card import Card, CardContent
from tools.attack import Attack


class Player:
    def __init__(self, player_id: int, hands: Hands, name: Optional[str] = None):
        self.player_id = player_id
        self.hands = hands
        self.name = name if name is not None else "Player{player_id}"

    def __repr__(self) -> str:
        return f"{self.name}: {self.hands}"

    def debug(self) -> str:
        return f"{self.name}: {self.hands.debug()}"

    def insert(self, card: Card) -> int:
        card = card.set_owner(self.player_id)
        inserted_hands, position = self.hands.insert(card=card)
        self.hands = inserted_hands
        return position

    def judge(self, attack: Attack) -> bool:
        return self.hands.judge(attack)

    def open(self, position: int) -> CardContent:
        self.hands, opened_card = self.hands.open(position=position)
        return opened_card

    def is_loser(self) -> bool:
        return self.hands.is_loser()
