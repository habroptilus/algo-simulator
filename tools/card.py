from typing import Optional
from tools.consts import COLORS, MIN_NUMBER, MAX_NUMBER


class CardContent:
    def __init__(self, color: str, number: int) -> None:
        if color not in COLORS:
            raise Exception(f"Invalid color: {color}")

        if number < MIN_NUMBER or number > MAX_NUMBER:
            raise Exception(f"Invalid number: {number}")
        self.color = color
        self.number = number

    def __eq__(self, __o: object) -> bool:
        return __o.color == self.color and __o.number == self.number

    def __lt__(self, __o: object) -> bool:
        if __o.number != self.number:
            return self.number < __o.number
        if self.color == 'B' and __o.color == 'W':
            return True
        return False

    def __repr__(self) -> str:
        return f"{self.color}{self.number:02}"


class Card:
    def __init__(self,
                 color: str,
                 number: int,
                 opened: bool = True,
                 owned_by: Optional[int] = None,
                 card_id: Optional[int] = None):
        self.__content = CardContent(color=color, number=number)
        self.opened = opened
        self.owned_by = owned_by
        self.card_id = card_id

    def get_content(self, referred_by: Optional[int] = None) -> CardContent:
        color = self.get_color()
        number = self.get_number(referred_by=referred_by)
        return CardContent(color=color, number=number)

    def get_color(self) -> str:
        return self.__content.color

    def get_number(self, referred_by: Optional[int] = None):
        if (not self.opened) and (referred_by != self.owned_by):
            raise Exception(
                f'The number is not available because the card is not opened and owned by Player{self.owned_by}, not Player{referred_by}.')
        return self.__content.number

    def open(self) -> 'Card':
        if self.opened:
            raise Exception(f'The card is already opened: {self}')
        return Card(color=self.__content.color, number=self.__content.number, opened=True, owned_by=self.owned_by, card_id=self.card_id)

    def __eq__(self, __o: object) -> bool:
        return (__o.__content == self.__content) and (__o.opened == self.opened) and (__o.owned_by == self.owned_by) and (__o.card_id == self.card_id)

    def __lt__(self, __o: object) -> bool:
        return self.__content < __o.__content

    def __repr__(self) -> str:
        if self.opened:
            return str(self.__content)
        return f"{self.__content.color}??"

    def debug(self) -> str:
        return str(self.__content)
