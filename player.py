import random
from collections import Counter

RANKS = list(range(1, 14))
SUITS = ["S", "H", "D", "C"]

def build_deck():
    return [(r, s) for r in RANKS for s in SUITS]

def card_value(card):
    return card[0]

def deal_cards(n):
    deck = build_deck()
    random.shuffle(deck)
    hands = [deck.pop() for _ in range(n)]
    return hands, deck

def should_swap(card, threshold, king_safe=True):
    v = card_value(card)
    if king_safe and v == 13:
        return False
    return v <= threshold

def play_round(num_players, threshold, king_safe=True):
    hands, deck = deal_cards(num_players)
    for i in range(num_players):
        c = hands[i]
        if i == num_players - 1:
            if should_swap(c, threshold, king_safe) and deck:
                hands[i] = deck.pop()
        else:
            if should_swap(c, threshold, king_safe):
                j = i + 1
                hands[i], hands[j] = hands[j], hands[i]
    vals = [card_value(c) for c in hands]
    m = min(vals)
    return vals.index(m)

def simulate(num_players, threshold, king_safe=True, rounds=10000000):
    losses = Counter()
    for _ in range(rounds):
        loser = play_round(num_players, threshold, king_safe)
        losses[loser] += 1
    return {p: losses[p] / rounds for p in range(num_players)}

def sweep_thresholds(num_players, king_safe=True, rounds=50000):
    results = {}
    for t in range(1, 13):
        results[t] = simulate(num_players, t, king_safe, rounds)
    return results

if __name__ == "__main__":
    random.seed(0)
    num_players = 4
    results = sweep_thresholds(num_players)
    for t, probs in results.items():
        print("threshold", t, probs)
