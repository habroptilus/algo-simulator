import argparse
from tools.game import Game
import random
from tools.logic import Human, MaxEntropy, EpsilonGreedy


def logic_factory(index, cpu: str, human_player: int):
    if index == human_player:
        return Human()
    if cpu == "e_greedy":
        return EpsilonGreedy(epsilon=0)
    if cpu == "max_entropy":
        return MaxEntropy()

    raise Exception(f"Invalid cpu: {cpu}.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Algo Simulator Parser')

    parser.add_argument('--human-player', '-hp', type=int, choices=[0, 1])
    parser.add_argument('--no-human', action='store_true')
    parser.add_argument('--cpu', default='e_greedy',
                        choices=["e_greedy", "max_entropy"])

    args = parser.parse_args()
    if args.no_human:
        human_player = -1
    elif args.human_player is None:
        human_player = random.randint(0, 1)
    else:
        human_player = args.human_player

    logics = [logic_factory(index=i, cpu=args.cpu,
                            human_player=human_player) for i in range(2)]
    game = Game(logics=logics)
    game.start()
