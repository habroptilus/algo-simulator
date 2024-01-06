from tools.player import Player
from tools.card import CardContent
from tools.attack import Attack
import random
from collections import defaultdict
from tools.consts import NUMBERS
from typing import List, Optional, Tuple


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

    # print(f"Extracted candidates with probability=1/{candidates_num}.")
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


def generate_tried_cards(card_id: int, history: List[Attack]) -> List[CardContent]:
    # Consider history.
    # Judge card's identity using card_id instead of position
    # because position is variable due to insertion.
    return [attack.card_content for attack in history
            if attack.card_id == card_id]


def generate_impossible_cards(player: Player, opened_cards: List[CardContent], new_card: Optional[CardContent]) -> List[CardContent]:
    # Consider cards owned by yourself.
    owned_by_self = player.hands.get_contents(referred_by=player.player_id)
    impossible_cards = opened_cards + owned_by_self
    if new_card is not None:
        impossible_cards.append(new_card)
    return impossible_cards


def get_attack(player: Player,
               opponents: List[Player],
               new_card: Optional[CardContent],
               opened_cards: List[CardContent],
               history: List[Attack],
               has_succeeded: bool,
               skip_second_attack: bool = False
               ) -> Optional[Attack]:

    if has_succeeded and skip_second_attack:
        # TODO: Add strategy for the case the previous attack is successful.
        # Currently, you can control by 'skip_second_attack' option.
        return
    attack_candidates: List[Attack] = []

    impossible_cards = generate_impossible_cards(
        player=player, opened_cards=opened_cards, new_card=new_card)

    for opponent in opponents:
        closed_cards = opponent.hands.get_closed_cards()
        opened_cards_locally = opponent.hands.get_opened_cards()

        for position, card_id, color in closed_cards:
            tried_cards = generate_tried_cards(
                card_id=card_id, history=history)
            impossible_cards_locally = impossible_cards + tried_cards
            # Consider bounds.
            lower_bound, upper_bound = get_bounds(
                opened_cards=opened_cards_locally, target=position)
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


def get_attack_from_input(player: Player, opponents: List[Player], new_card: Optional[CardContent], has_succeeded: bool):
    if new_card is not None:
        print(f"Draw: {new_card}")
    print(f"Your cards: {player.hands.debug()}")
    while True:
        inputs = input(
            "Enter '[position] [card]' or blank. > ").split()
        if len(inputs) == 0:
            if has_succeeded:
                return
            print(
                "You can't skip your next attack because your attack has not succeeded yet.")
            continue
        if len(inputs) <= 1 or len(inputs) >= 4:
            print(
                "Invalid inputs. The format should be '[position] [card]' or blank.")
            continue
        try:
            position = int(inputs[0])
        except Exception:
            continue
        card_content = inputs[1]
        target_player_id = 0
        if len(inputs) == 2 and len(opponents) > 1:
            print("Multi opponents requires target player id as third argument.")
            continue
        if len(inputs) == 3:
            target_player_id = int(inputs[2])
        if len(card_content) <= 1:
            continue

        # parse card_content
        color = card_content[0].upper()
        number = int(card_content[1:])

        opponent = opponents[target_player_id]
        card = opponent.hands.cards[position]
        if card.opened:
            print("Specified card has already been opened!")
            continue
        break

    card_id = opponent.hands.cards[position].card_id
    return Attack(
        position=position,
        color=color,
        number=number,
        attacked_to=opponent.player_id,
        attacked_by=player.player_id,
        card_id=card_id)
