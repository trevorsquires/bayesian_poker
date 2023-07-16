from treys import Card, Evaluator


class MyEvaluator:
    def __init__(self):
        self.evaluator = Evaluator()

    def evaluate_hand(self, hand, board):
        # Convert cards to trey cards
        trey_hand = [Card.new(card) for card in hand]
        trey_board = [Card.new(card) for card in board]

        # Evaluate hand strength
        strength = self.evaluator.evaluate(trey_board, trey_hand)

        return strength
