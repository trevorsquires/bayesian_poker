from src.simulator import naive_strategy

suits = ['♦', '♥', '♠', '♣']
ranks = ['A', 'K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2']
deck = [rank + suit for suit in suits for rank in ranks]

hand = ['A♥', 'A♦']
no_pairs = [[card1, card2] for card1 in deck for card2 in deck if ranks.index(card1[:-1]) > ranks.index(card2[:-1])]
pocket_pairs = [[card1, card2] for card1 in deck for card2 in deck
                if (ranks.index(card1[:-1]) == ranks.index(card2[:-1]))
                and (suits.index(card1[-1]) > suits.index(card2[-1]))]
all_hands = no_pairs + pocket_pairs
opp_range = [(hand, 1/len(all_hands)) for hand in all_hands]

board = []


print(naive_strategy(opp_range, hand, 0, board, 0))