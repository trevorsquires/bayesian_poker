from statistics import mode

class Evaluator:
    def __init__(self, deck_config):
        self.suits = deck_config['suits']
        self.ranks = deck_config['ranks']

    def evaluate_hand(self, hole_cards, community_cards):
        all_cards = hole_cards + community_cards
        best_hand = {'rank': -1, 'tiebreaker': -1}

        # Iterate over all possible 5-card combinations
        for i in range(len(all_cards)):
            for j in range(i + 1, len(all_cards)):
                hand = all_cards[:i] + all_cards[i + 1:j] + all_cards[j + 1:]
                rank, tiebreaker = self._get_hand_rank(hand)
                if (rank == best_hand['rank'] and tiebreaker < best_hand['tiebreaker']) or rank > best_hand['rank']:
                    best_hand = {
                        'rank': rank,
                        'cards': hand[:],
                        'tiebreaker': tiebreaker
                    }
        return best_hand

    def _get_hand_rank(self, hand):
        royal_flush_bool, tiebreaker = self._is_royal_flush(hand)
        if royal_flush_bool:
            return 9, tiebreaker

        straight_flush_bool, tiebreaker = self._is_straight_flush(hand)
        if straight_flush_bool:
            return 8, tiebreaker

        quads_bool, tiebreaker = self._is_quads(hand)
        if quads_bool:
            return 7, tiebreaker

        full_house_bool, tiebreaker = self._is_full_house(hand)
        if full_house_bool:
            return 6, tiebreaker

        flush_bool, tiebreaker = self._is_flush(hand)
        if flush_bool:
            return 5, tiebreaker

        straight_bool, tiebreaker = self._is_straight(hand)
        if straight_bool:
            return 4, tiebreaker

        set_bool, tiebreaker = self._is_set(hand)
        if set_bool:
            return 3, tiebreaker

        two_pair_bool, tiebreaker = self._is_two_pair(hand)
        if two_pair_bool:
            return 2, tiebreaker

        one_pair_bool, tiebreaker = self._is_one_pair(hand)
        if one_pair_bool:
            return 1, tiebreaker
        return 0, -1

    def _is_royal_flush(self, hand):
        return self._is_straight_flush(hand) and 'A' in hand and 'K' in hand, min([self.ranks.index(card[:-1]) for card in hand])

    def _is_straight_flush(self, hand):
        return self._is_flush(hand)[0] and self._is_straight(hand)[0], min([self.ranks.index(card[:-1]) for card in hand])

    def _is_quads(self, hand):
        return any(hand.count(rank) == 4 for rank in self.ranks), mode([self.ranks.index(card[:-1]) for card in hand])

    def _is_full_house(self, hand):
        # If you do not have quads and you only have 2 ranks, you have a full house.  Return true and the rank
        ranks = [card[:-1] for card in hand]
        unique_ranks = set(ranks)
        if len(unique_ranks) == 2:
            for rank in self.ranks:
                if hand.count(rank) == 3:
                    return True, rank
        return False, None

    def _is_flush(self, hand):
        # All suits must be the same
        return all(card[1] == hand[0][1] for card in hand), min([self.ranks.index(card[:-1]) for card in hand])

    def _is_straight(self, hand):
        ranks = [card[:-1] for card in hand]
        unique_ranks = set(ranks)
        sorted_ranks = sorted(ranks, key=lambda x: self.ranks.index(x))
        if len(unique_ranks) == 5:
            if self.ranks.index(sorted_ranks[-1]) - self.ranks.index(sorted_ranks[0]) == 4:
                return True, min([self.ranks.index(card[:-1]) for card in hand])
            if sorted_ranks[0] == 'A' and sorted_ranks[1] == '5' and sorted_ranks[-1] == '2':
                return True, self.ranks.index('5')
            return False, None
        else:
            return False, None

    def _is_set(self, hand):
        for rank in self.ranks:
            if [card[:-1] for card in hand].count(rank) == 3:
                return True, rank
        return False, None

    def _is_two_pair(self, hand):
        pairs = [rank for rank in self.ranks if [card[:-1] for card in hand].count(rank) == 2]
        return len(pairs) == 2, None if len(pairs) != 2 else max(pairs)

    def _is_one_pair(self, hand):
        # Check for a pair of cards in descending order.  If a match is found, return true and the rank
        for rank in self.ranks:
            if [card[:-1] for card in hand].count(rank) == 2:
                return True, rank
        return False, None

