from typing import Optional
from tools.card_list import Hands


class Player:
    def __init__(self, player_id: int, hands: Hands, name: Optional[str] = None):
        self.player_id = player_id
        self.hands = hands
        self.name = name if name is not None else "Player{player_id}"

    def __repr__(self) -> str:
        return f"{self.name}: {self.hands}"

    def debug(self) -> str:
        return f"{self.name}: {self.hands.debug()}"
