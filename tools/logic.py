import itertools
from tools.player import Player
from tools.card import CardContent, Card
from tools.attack import Attack
from tools.card_list import SimulationHands, Hands
import random
from collections import defaultdict
from tools.consts import NUMBERS
from typing import List, Optional, Tuple, Dict, Any
import numpy as np
import copy


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


def maximaize_probability(attack_candidates: List[Tuple[Attack, float]]) -> Tuple[List[Attack], float]:
    max_proba = 0
    attacks = []
    for attack, proba in attack_candidates:
        if max_proba < proba:
            attacks = [(attack, proba)]
            max_proba = proba
        elif abs(max_proba - proba) <= 0.0001:
            attacks.append((attack, proba))
    return attacks, max_proba


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


def generate_tried_cards(card_id: Optional[int], history: List[Attack]) -> List[CardContent]:
    # Consider history.
    # Judge card's identity using card_id instead of position
    # because position is variable due to insertion.
    return [attack.card_content for attack in history
            if attack.card_id == card_id]


def generate_impossible_cards(opened_cards: List[CardContent], new_card: Optional[CardContent] = None, player: Optional[Player] = None) -> List[CardContent]:
    impossible_cards = list(opened_cards)
    if player is not None:
        owned_by_self = player.hands.get_contents(referred_by=player.player_id)
        impossible_cards += owned_by_self
    if new_card is not None:
        impossible_cards.append(new_card)
    return impossible_cards


def get_local_candidates(card_id: Optional[int], history: List[Attack], impossible_cards: List[CardContent],
                         opened_cards_locally: List[CardContent], color: str, position: int) -> List[CardContent]:
    tried_cards = generate_tried_cards(
        card_id=card_id, history=history)
    impossible_cards_locally = impossible_cards + tried_cards
    # Consider bounds.
    lower_bound, upper_bound = get_bounds(
        opened_cards=opened_cards_locally, target=position)
    return apply_filters(color=color, impossible_cards=impossible_cards_locally,
                         lower_bound=lower_bound, upper_bound=upper_bound)


def simulate_if_insert_directly(new_card, player, opened_cards, history):
    card = Card(color=new_card.color, number=new_card.number,
                opened=False)
    inserted_hands, position = player.hands.insert(card=card)
    impossible_cards = generate_impossible_cards(opened_cards=opened_cards)
    opened_cards_locally = inserted_hands.get_opened_cards()
    local_candidate = get_local_candidates(
        card_id=None, history=history, impossible_cards=impossible_cards,
        opened_cards_locally=opened_cards_locally, color=card.get_color(), position=position)
    return len(local_candidate)


def calculate_hand_candidates(player: Player, opened_cards: List[CardContent], new_card: Optional[CardContent],
                              opponents: List[Player], history: List[Attack]) -> List[List[SimulationHands]]:
    impossible_cards = generate_impossible_cards(
        player=player, opened_cards=opened_cards, new_card=new_card)

    opponent_closed_positions: Dict[int, List[int]] = defaultdict(list)
    local_candidates_list: List[List[CardContent]] = []
    for opponent in opponents:
        closed_cards = opponent.hands.get_closed_cards()
        opened_cards_locally = opponent.hands.get_opened_cards()
        for position, card_id, color in closed_cards:
            local_candidates: List[CardContent] = get_local_candidates(
                card_id=card_id, history=history, impossible_cards=impossible_cards,
                opened_cards_locally=opened_cards_locally, color=color, position=position)

            opponent_closed_positions[opponent.player_id].append(position)
            local_candidates_list.append(local_candidates)

    return enumerate_candidates(
        local_candidates_list, opponent_closed_positions, opponents)


def estimate_self_entropy(candidate_hands_list, opponents, player, opened_cards, new_card, history, max_samples: int = 1):
    entropy_list_opened = []
    entropy_list_closed = []
    # reduce complexty
    sampled_hands_list = random.sample(
        candidate_hands_list, min(max_samples, len(candidate_hands_list)))

    for candidate_hands in sampled_hands_list:
        # assume that single opponent
        # TODO: support multi opponents
        assert len(candidate_hands) == 1
        for tentative_attacker_id, tentative_hand in candidate_hands:
            print(tentative_hand)
            # set candidate_hand to opponent
            opponents_sim = copy.deepcopy(opponents)
            opponent_sim = opponents_sim[0]
            opponent_sim.hands = Hands(tentative_hand.cards)
            # set opponent to tentative attacker
            tentative_attacker = opponent_sim
            # set player to original attacker
            original_attacker = copy.copy(player)
            # calculate hand_candidates of before state
            before_num = len(calculate_hand_candidates(
                player=tentative_attacker, opened_cards=opened_cards, new_card=None, opponents=[original_attacker], history=history))

            # calculate hand_candidates of after state with not opened new_card
            closed_card = Card(color=new_card.color,
                               number=new_card.number, opened=False)
            inserted_at = original_attacker.insert(closed_card)
            after_num_closed = len(calculate_hand_candidates(
                player=tentative_attacker, opened_cards=opened_cards, new_card=None, opponents=[original_attacker], history=history))

            # calculate hand_candidates of after state with opened new_card
            original_attacker.open(position=inserted_at)
            after_num_opened = len(calculate_hand_candidates(
                player=tentative_attacker, opened_cards=opened_cards, new_card=None, opponents=[original_attacker], history=history))

            print(f"Not Open: {before_num} -> {after_num_closed}")
            print(f"Open: {before_num} -> {after_num_opened}")
            entropy_list_opened.append(np.log(before_num/after_num_opened))
            entropy_list_closed.append(np.log(before_num/after_num_closed))

    entropy_opened = sum(entropy_list_opened)/len(entropy_list_opened)
    entropy_closed = sum(entropy_list_closed)/len(entropy_list_closed)

    return entropy_opened, entropy_closed


def get_attack(player: Player,
               opponents: List[Player],
               new_card: Optional[CardContent],
               opened_cards: List[CardContent],
               history: List[Attack],
               has_succeeded: bool,
               skip_proba: float = 0,
               maximize_entropy_strategy: bool = True,
               ) -> Tuple[Optional[Attack], Optional[Dict[str, Any]]]:
    if has_succeeded:
        if random.random() <= skip_proba:
            # skip the next attack
            return None, None
    meta = {}
    # enumerate hands candidates for opponents
    candidate_hands_list: List[List[SimulationHands]] = calculate_hand_candidates(
        player=player, opened_cards=opened_cards, new_card=new_card,
        opponents=opponents, history=history)

    print(f"Hand candidates: {len(candidate_hands_list)}")

    attacks_with_proba = transform_candidates_from_hand_to_attack(
        candidate_hands_list=candidate_hands_list, opponents=opponents, player=player)

    print(f"Attack candidates (Overall): {len(attacks_with_proba)}")

    if maximize_entropy_strategy:
        print("Maximize entropy.")
        if has_succeeded:
            # if you can skip, add skip option to candidates.
            attacks_with_proba.append((None, None))
        attack_candidates, entropy = maximize_entropy(attacks_with_proba=attacks_with_proba,
                                                      candidate_hands_list=candidate_hands_list, opponents=opponents,
                                                      player=player, opened_cards=opened_cards, new_card=new_card, history=history)
        print(f"Entropy: {entropy:.2f}")
        maximize_proba_results, _ = maximaize_probability(
            attack_candidates=attacks_with_proba)
        if not(set(maximize_proba_results) <= set(attack_candidates)):
            print(f"Strategy entropy : {attack_candidates}")
            print(f"Strategy probability : {maximize_proba_results}")
            meta["different_between_strategies"] = True
        else:
            meta["different_between_strategies"] = False
    else:
        print("Maxmize probability.")
        attack_candidates, proba = maximaize_probability(
            attack_candidates=attacks_with_proba)
        print(f"Probability: {proba:.2f}")

    # choose attacks to maxmize success probability
    print(f"Attack candidates: {len(attack_candidates)}")

    # sample an attack.
    chosen_attack, chosen_proba = random.choice(attack_candidates)
    print(f"Probability of Success: {int(chosen_proba*100):.1f}%")
    meta["proba"] = chosen_proba
    return chosen_attack, meta


def maximize_entropy(attacks_with_proba, candidate_hands_list, opponents, player,
                     opened_cards, new_card, history) -> Tuple[Optional[List[Tuple[Attack, float]]], float]:
    if len(attacks_with_proba) == 0:
        return None, 0
    max_gain = 0
    max_attacks = []
    entropy_opened, entropy_closed = estimate_self_entropy(candidate_hands_list=candidate_hands_list, opponents=opponents,
                                                           player=player, opened_cards=opened_cards, new_card=new_card,
                                                           history=history)

    for attack, p in attacks_with_proba:
        if attack is None:
            # the case of skip
            entropy_gain = - entropy_closed
            print(entropy_gain)
        else:
            filtered = [
                candidate_hands for candidate_hands in candidate_hands_list for opponent, hands in candidate_hands
                if (opponent == attack.attacked_to) and (hands.cards[attack.position].get_content() == attack.card_content)]

            # copy
            opponents_sim = copy.deepcopy(opponents)
            for opponent_sim in opponents_sim:
                if opponent_sim.player_id == attack.attacked_to:
                    opponent_sim.open(position=attack.position)

            next_attacks = transform_candidates_from_hand_to_attack(
                candidate_hands_list=filtered, opponents=opponents_sim, player=player)
            # Skip can be chosen after success of attacks
            next_attacks.append((None, None))

            _, descendant_entropy = maximize_entropy(attacks_with_proba=next_attacks,
                                                     candidate_hands_list=filtered, opponents=opponents_sim,
                                                     player=player, opened_cards=opened_cards, new_card=new_card, history=history)

            if p == 1:
                entropy_gain = descendant_entropy
            else:
                entropy_gain = p * (- np.log(p) + descendant_entropy) + \
                    (1-p)*(-np.log(1-p) - entropy_opened)

        if max_gain < entropy_gain:
            max_gain = entropy_gain
            max_attacks = [(attack, p)]
        elif abs(max_gain-entropy_gain) < 0.0001:
            max_attacks.append((attack, p))

    return max_attacks, max_gain


def transform_candidates_from_hand_to_attack(candidate_hands_list, opponents, player):
    # get attacks with probability
    counter: Dict[Tuple[int, int], Dict[str, int]
                  ] = defaultdict(lambda: defaultdict(int))
    for sim_hands_list in candidate_hands_list:
        for opponent_id, sim_hands in sim_hands_list:
            for position, card in enumerate(sim_hands.cards):
                counter[(opponent_id, position)][str(card.get_content())] += 1

    return get_attacks_with_proba(
        counter=counter, opponents=opponents, player=player)


def get_attacks_with_proba(counter: Dict[Tuple[int, int], Dict[str, int]],
                           opponents: List[Player], player: Player) -> List[Tuple[Attack, float]]:
    attacks_with_proba: List[Tuple[Attack, float]] = []
    for opponent in opponents:
        closed_cards = opponent.hands.get_closed_cards()
        for position, card_id, _ in closed_cards:
            inner_counter = counter[(opponent.player_id, position)]
            denominator = sum([freq for freq in inner_counter.values()])
            for card_content, count in inner_counter.items():
                attack = Attack(
                    card_id=card_id,
                    position=position,
                    color=card_content[0],
                    number=int(card_content[1:]),
                    attacked_to=opponent.player_id,
                    attacked_by=player.player_id
                )
                proba = count / denominator
                attacks_with_proba.append((attack, proba))
    return attacks_with_proba


def enumerate_candidates(local_candidates_list: List[List[CardContent]],
                         opponent_closed_positions: Dict[int, List[int]],
                         opponents: List[Player]) -> List[List[SimulationHands]]:
    fuga = list(itertools.product(*local_candidates_list))
    results: List[List[SimulationHands]] = []
    for card_contents in fuga:
        sim_hands_list = []
        for i, (opponent_id, positions) in enumerate(opponent_closed_positions.items()):
            tmp = [
                opponent for opponent in opponents if opponent.player_id == opponent_id]
            if len(tmp) == 0:
                raise Exception()
            opponent = tmp[0]
            sim_hands = SimulationHands(cards=opponent.hands.cards)
            for j, position in enumerate(positions):
                content = card_contents[i+j]
                sim_hands = sim_hands.overwrite(
                    position=position, content=content)
            sim_hands_list.append((opponent_id, sim_hands))
        if all([sim_hands.is_valid() for _, sim_hands in sim_hands_list]):
            results.append(sim_hands_list)
    return results


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
