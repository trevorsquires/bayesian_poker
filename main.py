"""
Simple script for running the Texas Hold'em Simulator

To run, simply specify the configurations and run the script. For players, you can specify which, if any, of the players
are user vs computer controlled.  You can also indicate whether a computer uses a Bayesian update to support its
decisions.
"""

from src.trey_evaluator import MyEvaluator
from src.player import Player
from src.simulator import TexasHoldemSimulator
from src.strategies import naive_strategy, user_strategy


def computer_player(win_pct, opp_range, hand, win_probabilities, amount_to_call, max_bet, pot):
    return naive_strategy(win_pct, amount_to_call, max_bet, pot)


def user_player(win_pct, opp_range, hand, win_probabilities, amount_to_call, max_bet, pot):
    return user_strategy(hand, win_probabilities, amount_to_call, max_bet, pot)


# Generate evaluate class
evaluator = MyEvaluator()

# Generate deck configurations and an evaluator function
suits = ['d', 'h', 'c', 's']
ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
deck_config = {'suits': suits, 'ranks': ranks, 'evaluator': evaluator.evaluate_hand}

# Set game configurations
big_blind = 10
big_blind_index = 0
game_config = {'big_blind': big_blind}

# Create players
stack_size = 1000
num_rounds = 100
players = [
    Player(strategy=computer_player, bayesian=True, name='Bayesian', stack=stack_size),
    Player(strategy=user_player, bayesian=False, name='Frequentist', stack=stack_size)
]

# Play a round
simulator = TexasHoldemSimulator(players, game_config, deck_config, clairvoyant=False)
simulator.run_simulation(num_rounds=num_rounds)


