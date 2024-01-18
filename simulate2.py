import argparse
from tools.game import Game
from tools.logic import EpsilonGreedy, MaxEntropy

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Algo Simulator Parser')

    parser.add_argument('--trials', '-t', type=int, default=10)

    args = parser.parse_args()

    results = []
    baseline = EpsilonGreedy(epsilon=0.1)
    proposed = MaxEntropy()

    logics_list = [[baseline, proposed], [proposed, baseline]]
    for logics in logics_list:
        game = Game(logics=logics, sleep_seconds=0)
        winners = []
        for _ in range(args.trials):
            outputs = game.start()
            winners.append(outputs["winner"])
        results.append((len(winners)-sum(winners))/len(winners))

    print(results)
