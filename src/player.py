class Player:
    def __init__(self, strategy, bayesian, name, stack):
        self.strategy = strategy
        self.bayesian = bayesian
        self.name = name
        self.chips = stack
        self.hand = []
        self.best_hand = None
        self.bet = 0
        self.opp_range = None

    def set_best_hand(self, hand):
        self.best_hand = hand

    def set_hole_cards(self, hand):
        self.hand = hand

    def take_action(self, win_pct, win_probabilities, amount_to_call, max_bet, pot):
        return self.strategy(
            win_pct=win_pct,
            opp_range=self.opp_range,
            hand=self.hand,
            win_probabilities=win_probabilities,
            amount_to_call=amount_to_call,
            max_bet=max_bet,
            pot=pot
        )

    def init_opp_range(self, win_probabilities):
        self.opp_range = {}
        num_hands = len(win_probabilities)
        for hand in win_probabilities:
            both_hands = {card for card in hand}.union({card for card in self.hand})
            if len(both_hands) < 4:
                self.opp_range[hand] = 0
            else:
                self.opp_range[hand] = 1/num_hands

    def update_opp_range(self, win_probabilities, bet, pot):
        perturbation = 0.000001
        normalization = 0
        for hand in win_probabilities.keys():
            win_pct = abs(win_probabilities[hand] - perturbation)
            desired_bet = pot * win_pct / (1 - win_pct)
            ratio = bet/desired_bet
            if ratio > 2:
                probability_of_evidence = 0.05
            elif ratio < 0.5:
                probability_of_evidence = 0.30
            else:
                probability_of_evidence = 0.65
            self.opp_range[hand] = self.opp_range[hand] * probability_of_evidence
            normalization += self.opp_range[hand]

        for hand in win_probabilities.keys():
            self.opp_range[hand] = self.opp_range[hand]/normalization
