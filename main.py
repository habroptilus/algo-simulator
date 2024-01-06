import random
from typing import List, Optional, Tuple
from collections import defaultdict
COLORS = ['B', 'W']
MIN_NUMBER = 0
MAX_NUMBER = 11
NUMBERS = list(range(MIN_NUMBER, MAX_NUMBER+1))
MAX_HANDS = 4
PLAYERS_NUM = 2
PLAYER_ID_LIST = list(range(PLAYERS_NUM))
START_ATTACKER = 0
MAX_TURNS = 100


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


class Attack:
    def __init__(self, card_id: int, position: int, color: str, number: int, attacked_to: int, attacked_by: int):
        self.card_id = card_id
        self.position = position
        self.card_content = CardContent(color=color, number=number)
        self.attacked_to = attacked_to
        self.attacked_by = attacked_by

    def __repr__(self) -> str:
        return f"{self.card_content} at {self.position} (Player{self.attacked_by} -> Player{self.attacked_to})"


class CardList:
    def __init__(self, cards: List[Card]):
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


class SimulationHands(CardList):
    def is_valid(self) -> bool:
        sorted_cards = sorted(self.cards)
        return sorted_cards == self.cards

    def overwrite(self, position: int, content: CardContent) -> 'SimulationHands':
        cards = list(self.cards)
        target_card = cards[position]
        cards[position] = Card(
            color=content.color, number=content.number, owned_by=target_card.owned_by, card_id=target_card.card_id)
        return SimulationHands(cards=cards)


class Deck(CardList):
    def __init__(self, colors: List[str], numbers: List[int]):
        cards = [Card(color=color, number=number, opened=False)
                 for color in colors for number in numbers]
        # shuffle
        self.cards: List[Card] = random.sample(cards, len(cards))
        self.card_id = 0

    def draw(self, player_id: int) -> Optional[Card]:
        if len(self.cards) == 0:
            return
        card = self.cards.pop()
        card.owned_by = player_id
        card.card_id = self.card_id
        self.card_id += 1
        return card


class Hands(CardList):
    def __init__(self, cards: List[Card]):
        self.cards: List[Card] = sorted(cards)

    def insert(self, card: Card) -> 'Hands':
        return Hands(self.cards + [card])

    def judge(self, attack: Attack) -> bool:
        target_card = self.cards[attack.position]
        if target_card.opened:
            raise Exception(
                f'The attacked card is already opened: {target_card}.')
        return target_card.get_content(referred_by=attack.attacked_to) == attack.card_content

    def open(self, position: int) -> 'Hands':
        # copy
        cards = list(self.cards)
        target_card = cards[position]
        target_card = target_card.open()
        cards[position] = target_card
        return Hands(cards=cards)

    def get_closed_cards(self) -> List[Tuple[int, int, str]]:
        return [(position, card.card_id, card.get_color()) for position, card in enumerate(self.cards) if not card.opened]

    def get_opened_cards(self) -> List[Tuple[int, CardContent]]:
        return [(position, card.get_content()) for position, card in enumerate(self.cards) if card.opened]

    def get_contents(self, referred_by: int) -> List[CardContent]:
        return [card.get_content(referred_by=referred_by) for card in self.cards]

    def is_loser(self) -> bool:
        return all([card.opened for card in self.cards])


class Player:
    def __init__(self, player_id: int, hands: Hands):
        self.player_id = player_id
        self.hands = hands

    def __repr__(self) -> str:
        return f"Player{self.player_id}: {self.hands}"

    def debug(self) -> str:
        return f"Player{self.player_id}: {self.hands.debug()}"


def init_player(deck: Deck, player_id: int, max_hands: int) -> Player:
    hands = Hands(cards=[deck.draw(player_id=player_id)
                  for _ in range(max_hands)])
    return Player(player_id=player_id, hands=hands)


def get_bounds(opened_cards: List[Tuple[int, CardContent]], target: int) -> Tuple[CardContent, CardContent]:
    # TODO: Update its logic to get more strict bounds.
    # e.g. In the case of "W04 B?? W?? W?? W09", candidates of B?? are "B05,B06,B07",
    # not "B05,B06,B07,B08,B09" which would be calculated by the current logic.
    # copy
    opened_cards = list(opened_cards)
    opened_cards.append((target, None))
    sorted_list = sorted(opened_cards, key=lambda x: x[0])

    index_target = sorted_list.index((target, None))

    # TODO: Refactor by defining new type instead of tuple
    lower_bound = sorted_list[index_target -
                              1][1] if index_target > 0 else None
    upper_bound = sorted_list[index_target +
                              1][1] if index_target < len(sorted_list) - 1 else None

    return lower_bound, upper_bound


def get_most_likely_attack_candidates(attack_candidates: List[Attack]) -> List[Attack]:
    counter = defaultdict(list)

    for attack in attack_candidates:
        counter[f"{attack.attacked_to}_{attack.position}"].append(attack)

    min_attacks = 1000000
    most_likely_candidates = []
    for _, attacks in counter.items():
        candidates_num = len(attacks)
        if candidates_num == min_attacks:
            most_likely_candidates += attacks
        elif candidates_num < min_attacks:
            most_likely_candidates = attacks

    print(f"Extracted candidates with probability=1/{candidates_num}.")
    return most_likely_candidates


def apply_filters(color: str, impossible_cards: List[CardContent],
                  lower_bound: Optional[CardContent], upper_bound: Optional[CardContent]):
    candidates = [CardContent(color=color, number=number)
                  for number in NUMBERS]

    if lower_bound is not None:
        candidates = [
            candidate for candidate in candidates if lower_bound < candidate]

    if upper_bound is not None:
        candidates = [
            candidate for candidate in candidates if candidate < upper_bound]

    return [candidate for candidate in candidates if (candidate not in impossible_cards)]


def generate_tried_cards(card_id, history):
    # Consider history.
    # Judge card's identity using card_id instead of position
    # because position is variable due to insertion.
    return [attack.card_content for attack in history
            if attack.card_id == card_id]


def generate_impossible_cards(player, opened_cards, new_card):
    # Consider cards owned by yourself.
    owned_by_self = player.hands.get_contents(referred_by=player.player_id)
    impossible_cards = opened_cards + owned_by_self
    if new_card is not None:
        impossible_cards.append(new_card)
    return impossible_cards


def get_attack(player: Player,
               opponents: List[Player],
               new_card: Optional[CardContent],
               all_opened_cards: List[CardContent],
               has_succeeded: bool,
               history: List[Attack],
               skip_second_attack: bool = False
               ) -> Optional[Attack]:

    if has_succeeded and skip_second_attack:
        # TODO: Add strategy for the case the previous attack is successful.
        # Currently, you can control by 'skip_second_attack' option.
        return
    attack_candidates: List[Attack] = []

    impossible_cards = generate_impossible_cards(
        player=player, opened_cards=all_opened_cards, new_card=new_card)

    for opponent in opponents:
        closed_cards = opponent.hands.get_closed_cards()
        opened_cards = opponent.hands.get_opened_cards()

        for position, card_id, color in closed_cards:
            tried_cards = generate_tried_cards(
                card_id=card_id, history=history)
            impossible_cards_locally = impossible_cards + tried_cards
            # Consider bounds.
            lower_bound, upper_bound = get_bounds(
                opened_cards=opened_cards, target=position)
            candidates = apply_filters(color=color, impossible_cards=impossible_cards_locally,
                                       lower_bound=lower_bound, upper_bound=upper_bound)
            attack_candidates += [
                Attack(
                    position=position,
                    color=candidate.color,
                    number=candidate.number,
                    attacked_to=opponent.player_id,
                    attacked_by=player.player_id,
                    card_id=card_id)
                for candidate in candidates]
    # Maximize success probability.
    most_likely_candidates = get_most_likely_attack_candidates(
        attack_candidates=attack_candidates)
    return random.choice(most_likely_candidates)


class Game:
    def __init__(self, colors, numbers, max_turns, start_attacker):
        self.colors = colors
        self.numbers = numbers
        self.max_turns = max_turns
        self.start_attacker = start_attacker

    def start(self):
        deck = Deck(colors=self.colors, numbers=self.numbers)

        players = [init_player(deck=deck, player_id=player_id,
                               max_hands=MAX_HANDS) for player_id in PLAYER_ID_LIST]
        history = []
        opened_cards = []
        losers = 0
        attacker = self.start_attacker
        for turn in range(self.max_turns):
            for player in players:
                print(player)
            player = players[attacker]
            print(f"Turn{turn+1} Attacker: Player{player.player_id}")
            opponents = [
                player for player in players if player.player_id != attacker]

            new_card = deck.draw(player_id=player.player_id)
            if new_card is None:
                print("deck is empty.")
            else:
                new_card_content = new_card.get_content(
                    referred_by=player.player_id)
                print(f"Draw: {new_card_content}")

            has_succeeded = False
            while True:
                attack = get_attack(
                    player=player,
                    opponents=opponents,
                    new_card=new_card_content,
                    all_opened_cards=opened_cards,
                    has_succeeded=has_succeeded,
                    history=history,
                )
                if attack is None:
                    if not has_succeeded:
                        raise Exception(
                            "You can't skip your next attack because your attack has not succeeded yet.")
                    print("Skip your next attack.")
                    break

                print(f"Attack: {attack}")
                # Apply attack
                history.append(attack)
                opponent = players[attack.attacked_to]
                result = opponent.hands.judge(attack=attack)
                if result:
                    print("Success!")
                    has_succeeded = True
                    opponent.hands = opponent.hands.open(
                        position=attack.position)
                    opened_cards.append(CardContent(
                        color=attack.card_content.color, number=attack.card_content.number))
                    # Judge whether the game is over or not
                    if opponent.hands.is_loser():
                        losers += 1
                        if losers == PLAYERS_NUM-1:
                            print(
                                f"The game is over! Winner: Player{player.player_id}.")
                            return player.player_id

                else:
                    print("Failed...")
                    if new_card is not None:
                        new_card.opened = True
                    break

            if new_card is not None:
                player.hands = player.hands.insert(new_card)

            # switch attacker
            attacker = (attacker+1) % PLAYERS_NUM


if __name__ == '__main__':
    game = Game(
        colors=COLORS, numbers=NUMBERS, max_turns=MAX_TURNS, start_attacker=START_ATTACKER
    )
    game.start()
