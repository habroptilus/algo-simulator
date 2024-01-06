from tools.card import CardContent


class Attack:
    def __init__(self, card_id: int, position: int, color: str, number: int, attacked_to: int, attacked_by: int):
        self.card_id = card_id
        self.position = position
        self.card_content = CardContent(color=color, number=number)
        self.attacked_to = attacked_to
        self.attacked_by = attacked_by

    def __repr__(self) -> str:
        return f"{self.card_content} at {self.position} (Player{self.attacked_by} -> Player{self.attacked_to})"
