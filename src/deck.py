import random


class Deck:
    def __init__(self, deck_config):
        self.deck_config = deck_config
        self.cards = [rank + suit for suit in self.deck_config['suits'] for rank in self.deck_config['ranks']]

    def pop_cards(self, num_cards):
        drawn_cards = random.sample(self.cards, num_cards)
        for card in drawn_cards:
            self.cards.remove(card)

        return drawn_cards

    def remove_cards(self, cards):
        for card in cards:
            self.cards.remove(card)

    def add_cards(self, cards):
        for card in cards:
            self.cards.append(card)
