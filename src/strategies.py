import random


def user_strategy(hand, win_probabilities, amount_to_call, max_bet, pot):
    print(f"You need to call {amount_to_call} to stay in the hand. Your max bet is {max_bet} and the pot size is {pot}")
    print(f"Your hand is {hand} and you have roughly a {win_probabilities[tuple(hand)]*100}% chance to win in a vacuum")
    return int(input("Enter your desired bet size: ").strip().lower())


def naive_strategy(win_pct, amount_to_call, max_bet, pot):
    if win_pct == 1:
        desired_bet = max_bet+1
    else:
        desired_bet = round(pot*win_pct/(1-win_pct))

    if desired_bet < amount_to_call:
        return 0  # if odds aren't good, fold
    elif desired_bet > max_bet:  # if odds are great, shove/put them all in
        return max_bet
    elif desired_bet < 2*amount_to_call:  # if odds are good, not great, just call
        return amount_to_call
    else:
        if random.random() < 0.25:
            return amount_to_call  # even if odds are great, sometimes disguise strength of hand
        else:
            return desired_bet  # if odds are great, raise


