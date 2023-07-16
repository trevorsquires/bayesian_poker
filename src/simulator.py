import random
from src.deck import Deck
"""
TODO LIST
    - Move things into more functions using the DRY and "1 job" principles
"""


class TexasHoldemSimulator:
    def __init__(self, players, game_config, deck_config):
        self.players = players
        self.game_config = game_config
        self.deck_config = deck_config

        self.hand_probabilities = {}
        self.big_blind_index = None
        self.remaining_player_ids = None
        self.folded_player_ids = None
        self.pot = None
        self.deck = None
        self.community_cards = []
        self.street = 0

    def create_deck(self):
        self.deck = Deck(self.deck_config)

    def sim_runouts(self, hand, opp_range, deck, it):
        total_probability = 0
        win_probability = 0
        for _ in range(it):  # Monte Carlo simulation
            # Simulate opponents cards
            opp_hand = deck.pop_cards(2)
            opp_hand_prob = opp_range[tuple(self.sort_hand(opp_hand))]

            # Simulate runout
            runout = deck.pop_cards(5 - len(self.community_cards))
            tmp_community = self.community_cards + runout

            # Rank hands
            my_strength = self.deck_config['evaluator'](hand, tmp_community)
            opp_strength = self.deck_config['evaluator'](opp_hand, tmp_community)

            # Update win totals (weighted by probability of drawing opponent hand)
            if my_strength < opp_strength:
                win_probability += opp_hand_prob
            total_probability += opp_hand_prob

            # Add cards back into deck
            deck.add_cards(opp_hand)
            deck.add_cards(runout)

        return win_probability/total_probability

    def eval_all_hands(self):
        deck = Deck(self.deck_config)
        deck.remove_cards(self.community_cards)

        # Compute all possible hands given the community cards on the board
        no_pairs = [[card1, card2] for card1 in deck.cards for card2 in deck.cards if
                    self.deck_config['ranks'].index(card1[:-1]) > self.deck_config['ranks'].index(card2[:-1])]
        pocket_pairs = [[card1, card2] for card1 in deck.cards for card2 in deck.cards
                        if (self.deck_config['ranks'].index(card1[:-1]) == self.deck_config['ranks'].index(card2[:-1]))
                        and (self.deck_config['suits'].index(card1[-1]) > self.deck_config['suits'].index(card2[-1]))]
        all_hands = no_pairs + pocket_pairs

        # For each valid hand, compute its approximate win percentage via a Monte Carlo simulation
        for hand in all_hands:
            # Assume user was dealt hand and compute win probability
            deck.remove_cards(hand)
            opp_range = {tuple(hand): 1/len(all_hands) for hand in all_hands}  # TODO need to remove some hands from all_hands
            self.hand_probabilities[tuple(hand)] = self.sim_runouts(hand, opp_range, deck, it=50)
            deck.add_cards(hand)

    def deal_hole_cards(self):
        for player in self.players:
            tmp_hand = self.deck.pop_cards(2)
            player.set_hole_cards(self.sort_hand(tmp_hand))
            player.init_opp_range(self.hand_probabilities)

    def deal_community_cards(self, num_cards):
        self.community_cards.extend(self.deck.pop_cards(num_cards))

    def preflop_betting_round(self, initial_bet):
        num_players = len(self.players)
        current_index = (self.big_blind_index + 1) % len(self.players)
        current_bet = initial_bet
        bettor_index = self.big_blind_index

        self.players[self.big_blind_index].bet = self.game_config['big_blind']

        while len(self.remaining_player_ids) > 1:
            current_player = self.players[current_index]
            other_player = self.players[int(not current_index)]

            if current_index not in self.folded_player_ids:
                amount_to_call = current_bet - current_player.bet
                print(f"\n{current_player.name}, it is your turn.")

                while True:
                    tmp_deck = Deck(self.deck_config)
                    tmp_deck.remove_cards(current_player.hand)
                    tmp_deck.remove_cards(self.community_cards)
                    win_pct = self.sim_runouts(current_player.hand, current_player.opp_range, tmp_deck, it=500)
                    print(f'{current_player.name} thinks that they win about {round(win_pct*100)}% of the time')
                    bet = current_player.take_action(win_pct, self.hand_probabilities, amount_to_call,
                                                     min([player.chips + amount_to_call for player in self.players] +
                                                         [current_player.chips]), self.pot)
                    if other_player.bayesian:
                        other_player.update_opp_range(self.hand_probabilities, bet, self.pot)
                    if bet < amount_to_call:
                        print(f"{current_player.name} folds.")
                        self.folded_player_ids.add(current_index)
                        self.remaining_player_ids.remove(current_index)
                        break

                    elif bet == amount_to_call:
                        current_player.chips -= amount_to_call
                        current_player.bet += amount_to_call
                        self.pot += amount_to_call
                        if bet != 0:
                            print(f"{current_player.name} calls {amount_to_call}.")
                        else:
                            print(f"{current_player.name} checks")
                        break

                    else:
                        current_player.chips -= bet
                        current_player.bet += bet
                        current_bet = current_player.bet
                        self.pot += bet
                        bettor_index = current_index
                        print(f"{current_player.name} raises to {current_bet}.")
                        break

            current_index = (current_index + 1) % num_players

            if current_index == bettor_index:
                break

        # Reset the current bets for all players
        for player in self.players:
            player.bet = 0

        self.street += 1

    def _facilitate_action(self, current_index, current_player, other_player, amount_to_call):
        # Request the action from the player
        tmp_deck = Deck(self.deck_config)
        tmp_deck.remove_cards(current_player.hand)
        tmp_deck.remove_cards(self.community_cards)
        win_pct = self.sim_runouts(current_player.hand, current_player.opp_range, tmp_deck, it=500)
        print(f'{current_player.name} thinks that they win about {round(win_pct * 100)}% of the time')
        bet = current_player.take_action(win_pct, self.hand_probabilities, amount_to_call,
                                         min([player.chips + amount_to_call for player in self.players] +
                                             [current_player.chips]), self.pot)

        # If the other player is a Bayesian player, update the opponent range
        if other_player.bayesian:
            other_player.update_opp_range(self.hand_probabilities, bet, self.pot)

        # Handle different cases of desired bet sizing
        if bet < amount_to_call:
            print(f"{current_player.name} folds.")
            self.folded_player_ids.add(current_index)
            self.remaining_player_ids.remove(current_index)
            return {'fold': True}

        elif bet == amount_to_call:
            current_player.chips -= amount_to_call
            current_player.bet += amount_to_call
            self.pot += amount_to_call
            if bet != 0:
                print(f"{current_player.name} calls {amount_to_call}.")
            else:
                print(f"{current_player.name} checks")
            return {}

        else:  # bet > amount_to_call means they have chosen to raise
            current_player.chips -= bet
            current_player.bet += bet
            self.pot += bet

            print(f"{current_player.name} raises to {current_player.bet}.")
            return{'new_bet': True, 'current_bet': current_player.bet, 'bettor_index': current_index}

    def _betting_round(self, preflop_bool):
        current_index = int(not self.big_blind_index)
        bettor_index = self.big_blind_index if preflop_bool else 0
        current_bet = self.game_config['big_blind'] if preflop_bool else 0

        if preflop_bool:
            self.players[self.big_blind_index].bet = self.game_config['big_blind']
            self.players[int(not self.big_blind_index)].bet = int(0.5*self.game_config['big_blind'])

        # Every player gets an opportunity to take action
        updates = {}
        for _ in range(2):
            # Define who's turn it is
            current_player = self.players[current_index]
            other_player = self.players[int(not current_index)]
            amount_to_call = current_bet - current_player.bet
            print(f"\n{current_player.name}, it is your turn.")

            # Facilitate action from current player
            updates = self._facilitate_action(current_index, current_player, other_player, amount_to_call)
            if updates.get('fold'):
                break
            current_bet = updates['current_bet'] if updates.get('new_bet') else current_bet
            bettor_index = updates['bettor_index'] if updates.get('new_bet') else bettor_index

            # Move to next player
            current_index = int(not current_index)

        if current_bet == 0:  # everyone checked postflop
            pass
        elif current_bet == self.game_config['big_blind'] and preflop_bool:  # everyone check preflop
            pass
        elif updates.get('fold'):
            pass
        else:  # someone must have bet and they are the bettor index
            while bettor_index != current_index:
                # Define who's turn it is
                current_player = self.players[current_index]
                other_player = self.players[int(not current_index)]
                amount_to_call = current_bet - current_player.bet
                print(f"\n{current_player.name}, it is your turn.")

                # Facilitate action from current player
                updates = self._facilitate_action(current_index, current_player, other_player, amount_to_call)
                current_bet = updates['current_bet'] if updates.get('new_bet') else current_bet
                bettor_index = updates['bettor_index'] if updates.get('new_bet') else bettor_index

                # Move to next player
                current_index = int(not current_index)

        # Reset the current bets for all players
        for player in self.players:
            player.bet = 0

        self.street += 1

    def play_round(self):
        self.create_deck()
        self.eval_all_hands()
        self.deal_hole_cards()
        self.big_blind_index = random.randint(0, len(self.players)-1)

        # Set up
        self.remaining_player_ids = set(range(len(self.players)))
        self.folded_player_ids = set()
        self.pot = self.game_config['big_blind']

        # Pre-flop betting round
        print(f"\n---------- Street: Pre-Flop ----------")
        self.players[self.big_blind_index].chips -= self.game_config['big_blind']
        self._betting_round(preflop_bool=True)

        if len(self.remaining_player_ids) > 1:
            # Flop
            self.deal_community_cards(num_cards=3)

            print(f"\n---------- Street: Flop ----------")
            print(f'The flop comes:{self.community_cards}\n')

            self.eval_all_hands()
            self._betting_round(preflop_bool=False)

            if len(self.remaining_player_ids) > 1:
                # Turn
                self.deal_community_cards(num_cards=1)

                print(f"\n---------- Street: Turn ----------")
                print(f'The turn card:{self.community_cards}\n')

                self.eval_all_hands()
                self._betting_round(preflop_bool=False)

                if len(self.remaining_player_ids) > 1:
                    # River
                    self.deal_community_cards(num_cards=1)

                    print(f"\n---------- Street: River ----------")
                    print(f'The river card:{self.community_cards}\n')

                    self.eval_all_hands()
                    self._betting_round(preflop_bool=False)

        self.determine_winner()
        self.print_player_chips()
        self.community_cards = []

    def determine_winner(self):
        showdown = False
        if len(self.remaining_player_ids) == 1:
            (best_player_id,) = self.remaining_player_ids
            best_player = self.players[best_player_id]
        else:
            # Evaluate hands for all players
            showdown = True
            best_rank = 10000
            best_player = None
            for player_id in self.remaining_player_ids:
                player = self.players[player_id]
                player.rank = self.deck_config['evaluator'](player.hand, self.community_cards)
                if player.rank < best_rank:
                    best_rank = player.rank
                    best_player = player

        best_player.chips += self.pot
        print(f'\n{best_player.name} has won the pot ', end='')
        if showdown:
            print(f'with {best_player.hand} ', end='')
        print(f'and has been awarded with {self.pot} chips')
        for player in self.players:
            print(f"{player.name}'s hand was {player.hand}")
        self.pot = 0

    def sort_hand(self, hand):
        card1 = hand[0]
        card2 = hand[1]
        rank1 = self.deck_config['ranks'].index(card1[0])
        rank2 = self.deck_config['ranks'].index(card2[0])
        if rank1 > rank2:
            return [card1, card2]
        if rank1 < rank2:
            return [card2, card1]
        else:
            suit1 = self.deck_config['suits'].index(card1[1])
            suit2 = self.deck_config['suits'].index(card2[1])
            if suit1 > suit2:
                return [card1, card2]
            else:
                return [card2, card1]

    def print_player_chips(self):
        print("\n---------- Player Chip Counts ----------")
        for player in self.players:
            print(f"{player.name}: {player.chips} chips")

    def run_simulation(self, num_rounds):
        for i in range(num_rounds):
            if min([player.chips for player in self.players]) == 0:
                break
            print(f"\n=============== Round {i+1} ===============")
            self.play_round()

