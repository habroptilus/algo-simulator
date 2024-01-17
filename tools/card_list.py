import random
from typing import Optional, Tuple
from tools.card import Card, CardContent
from tools.attack import Attack


class CardList:
    def __init__(self, cards: list[Card]):
        self.cards = cards

    def __repr__(self) -> str:
        return " ".join([str(card) for card in self.cards])

    def __len__(self) -> str:
        return len(self.cards)

    def __eq__(self, __o: object) -> bool:
        if len(self) != len(__o):
            return False
        for a, b in zip(self.cards, __o.cards):
            if a != b:
                return False
        return True

    def debug(self) -> str:
        return " ".join([card.debug() for card in self.cards])

    def is_unique(self) -> bool:
        return len(set([str(card.get_content_id()) for card in self.cards])) == len(self.cards)


class SimulationHands(CardList):
    def __init__(self, cards: list[Card]):
        # open all cards
        return super().__init__([card.open() if not card.opened else card for card in cards])

    def is_valid(self) -> bool:
        return self.is_sorted() and self.is_unique()

    def is_sorted(self) -> bool:
        sorted_cards = sorted(self.cards)
        return sorted_cards == self.cards

    def overwrite(self, position: int, content: CardContent) -> 'SimulationHands':
        cards = list(self.cards)
        target_card = cards[position]
        cards[position] = Card(
            color=content.color, number=content.number, owned_by=target_card.owned_by, card_id=target_card.card_id)
        return SimulationHands(cards=cards)


class Deck(CardList):
    def __init__(self, colors: list[str], numbers: list[int]):
        cards = [Card(color=color, number=number, opened=False, card_id=i+j)
                 for i, color in enumerate(colors) for j, number in enumerate(numbers)]
        # shuffle
        self.cards: list[Card] = random.sample(cards, len(cards))

    def draw(self, player_id: int) -> Optional[Card]:
        if len(self.cards) == 0:
            return
        card = self.cards.pop()
        card = card.set_owner(player_id=player_id)
        return card


class Hands(CardList):
    def __init__(self, cards: list[Card]):
        self.cards: list[Card] = sorted(cards)

    def insert(self, card: Card) -> Tuple['Hands', int]:
        hands = Hands(cards=self.cards + [card])
        if not hands.is_unique():
            raise Exception(
                f"Inserted card violates hands' uniqueness: {card}")
        position = hands.find(card=card)
        assert position is not None

        return hands, position

    def find(self, card: Card) -> Optional[int]:
        if card not in self.cards:
            return

        return self.cards.index(card)

    def judge(self, attack: Attack) -> bool:
        target_card = self.cards[attack.position]
        if target_card.opened:
            raise Exception(
                f'The attacked card is already opened: {target_card}.')
        return target_card.get_content(referred_by=attack.attacked_to) == attack.card_content

    def open(self, position: int) -> Tuple['Hands', CardContent]:
        # copy
        cards = list(self.cards)
        target_card = cards[position]
        target_card = target_card.open()
        cards[position] = target_card
        return Hands(cards=cards), target_card.get_content()

    def get_closed_cards(self) -> list[Tuple[int, int, str]]:
        return [(position, card.card_id, card.get_color()) for position, card in enumerate(self.cards) if not card.opened]

    def get_opened_cards(self) -> list[Tuple[int, CardContent]]:
        return [(position, card.get_content()) for position, card in enumerate(self.cards) if card.opened]

    def get_contents(self, referred_by: int) -> list[CardContent]:
        return [card.get_content(referred_by=referred_by) for card in self.cards]

    def is_loser(self) -> bool:
        return all([card.opened for card in self.cards])
