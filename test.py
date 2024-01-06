
import unittest
from tools.card_list import Hands, SimulationHands
from tools.card import Card,  CardContent


class HandsTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_init(self):
        card_contents = [('W', 4), ('W', 1), ('B', 1)]
        expected_contents = [('B', 1), ('W', 1), ('W', 4)]
        hands = Hands(cards=[Card(color=color, number=number)
                             for color, number in card_contents])

        expected = Hands(cards=[Card(color=color, number=number)
                                for color, number in expected_contents])
        self.assertEqual(expected, hands)


class SimulationHandsTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_init(self):
        card_contents = [('W', 4), ('W', 1), ('B', 1)]
        invalid_hands = SimulationHands(cards=[Card(color=color, number=number)
                                               for color, number in card_contents])
        self.assertFalse(invalid_hands.is_valid(), invalid_hands)

    def test_overwrite(self):
        card_contents = [('W', 4), ('W', 1), ('B', 1)]
        hands = SimulationHands(cards=[Card(color=color, number=number)
                                       for color, number in card_contents])
        old = CardContent('W', 1)
        expected = CardContent('B', 10)
        position = 1
        hands_new = hands.overwrite(position, expected)

        self.assertEqual(expected, hands_new.cards[position].get_content())
        self.assertEqual(old, hands.cards[position].get_content())


if __name__ == "__main__":
    unittest.main()
