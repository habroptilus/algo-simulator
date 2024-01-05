import random
from typing import List, Optional
COLORS = ['B', 'W']
MIN_NUMBER = 0
MAX_NUMBER = 11
NUMBERS = list(range(MAX_NUMBER+1))
MAX_HANDS = 4


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
    def __init__(self, color: str, number: int, opened: bool = False, owned_by: Optional[int] = None):
        self.__content = CardContent(color=color, number=number)
        self.opened = opened
        self.owned_by = owned_by

    def get_content(self, referred_by: int) -> CardContent:
        color = self.get_color()
        number = self.get_number(referred_by=referred_by)
        return CardContent(color=color, number=number)

    def get_color(self) -> str:
        return self.__content.color

    def get_number(self, referred_by: int):
        if (referred_by != self.owned_by) and (not self.opened):
            raise Exception(
                f'The number is not available because the card is not opened and owned by Player{self.owned_by}, not Player{referred_by}.')
        return self.__content.number

    def open(self):
        if self.opened:
            raise Exception(f'The card is already opend: {self}')
        self.opened = True

    def __eq__(self, __o: object) -> bool:
        return __o.__content == self.__content

    def __lt__(self, __o: object) -> bool:
        return self.__content < __o.__content

    def __repr__(self) -> str:
        if self.opened:
            return str(self.__content)
        return f"{self.__content.color}??"

    def debug(self) -> str:
        return str(self.__content)


class CardList:
    def __init__(self, cards: List[Card]):
        self.cards = cards

    def __repr__(self) -> str:
        return " ".join([str(card) for card in self.cards])

    def __len__(self) -> str:
        return len(self.cards)

    def debug(self) -> str:
        return " ".join([card.debug() for card in self.cards])


class Deck(CardList):
    def __init__(self, colors: List[str], numbers: List[int]):
        cards = [Card(color=color, number=number)
                 for color in colors for number in numbers]
        self.cards: List[Card] = random.sample(cards, len(cards))

    def draw(self, player_id: int):
        card = self.cards.pop()
        card.owned_by = player_id
        return card


class Attack:
    def __init__(self, position: int, color: str, number: int, attacked_to: int):
        self.position = position
        self.card_content = CardContent(color=color, number=number)
        self.attacked_to = attacked_to


class Hands(CardList):
    def __init__(self, cards: List[Card]):
        self.cards: List[Card] = sorted(cards)

    def add(self, card: Card):
        self.cards.append(card)
        self.cards = sorted(self.cards)

    def judge(self, attack: Attack) -> bool:
        target_card = self.cards[attack.position]
        if target_card.opened:
            raise Exception(
                f'The attacked card is already opend: {target_card}.')
        return target_card.get_content(referred_by=attack.attacked_to) == attack.card_content

    def open(self, position: int):
        target_card = self.cards[position]
        # original item is overwritten.
        target_card.open()


class Player:
    def __init__(self, player_id: int, hands: Hands):
        self.player_id = player_id
        self.hands = hands

    def __repr__(self) -> str:
        return f"Player{self.player_id}\n{self.hands}"


class History:
    def __init__(self, attacks: Optional[List[Attack]]):
        if attacks is not None:
            self.attacks = attacks
        self.attacks = []

    def add(self, attack: Attack):
        self.attacks.append(attack)


def init_player(deck: Deck, player_id: int, max_hands: int) -> Player:
    hands = Hands(cards=[deck.draw(player_id=player_id)
                  for _ in range(max_hands)])
    return Player(player_id=player_id, hands=hands)


if __name__ == '__main__':
    deck = Deck(colors=COLORS, numbers=NUMBERS)

    player_id_list = [1, 2]
    players = [init_player(deck=deck, player_id=player_id,
                           max_hands=MAX_HANDS) for player_id in player_id_list]

    player: Player = players[0]
    opponent: Player = players[1]

    new_card = deck.draw(player_id=player.player_id)
    print(new_card.get_content(referred_by=player.player_id))
    # TODO: Generate Attack via calculation
    attack = Attack(position=0, color='B', number=2,
                    attacked_to=opponent.player_id)
    result = opponent.hands.judge(attack=attack)
    if result:
        opponent.hands.open(position=attack.position)
        # TODO: Implement Re-attack process after attack success.
    else:
        new_card.opened = True

    player.hands.add(new_card)

    print(player)
    print(player.hands.debug())
