from src.trey_evaluator import MyEvaluator
from src.player import Player
from src.simulator import TexasHoldemSimulator
from src.strategies import naive_strategy, user_strategy


def poker_strat(win_pct, opp_range, hand, win_probabilities, amount_to_call, max_bet, pot):
    return naive_strategy(win_pct, amount_to_call, max_bet, pot)


def user_strat(win_pct, opp_range, hand, win_probabilities, amount_to_call, max_bet, pot):
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
players = [
    Player(strategy=poker_strat, bayesian=True, name='Bayesian', stack=stack_size),
    Player(strategy=poker_strat, bayesian=False, name='Frequentist', stack=stack_size)
]

# Play a round
simulator = TexasHoldemSimulator(players, game_config, deck_config)
simulator.run_simulation(num_rounds=100)


