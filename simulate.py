import argparse
from tools.game import Game
from tools.logic import EpsilonGreedy

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Algo Simulator Parser')

    parser.add_argument('--trials', '-t', type=int, default=10)

    args = parser.parse_args()

    epsilons = [0, 0.1, 0.5, 1]
    results = {}

    for e1 in epsilons:
        for e2 in epsilons:
            logics = [EpsilonGreedy(epsilon=e1),
                      EpsilonGreedy(epsilon=e2)]
            game = Game(logics=logics, sleep_seconds=0)
            winners = []
            for _ in range(args.trials):
                outputs = game.start()
                winners.append(outputs["winner"])

            results[f"{e1}_{e2}"] = (len(winners)-sum(winners))/len(winners)

    print(results)
