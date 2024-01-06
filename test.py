
import unittest
from main import Hands, Card


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

    def test_is_valid(self):
        card_contents = [('W', 4), ('W', 1), ('B', 1)]
        hands = Hands(cards=[Card(color=color, number=number)
                             for color, number in card_contents])
        hands = hands.insert(Card(color='B', number=4))
        self.assertTrue(hands.is_valid(), hands)


if __name__ == "__main__":
    unittest.main()
