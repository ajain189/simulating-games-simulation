import random

def play_round(num_players, switch_threshold):
    # ----- Setup -----
    deck = []
    for v in range(1,14):
        deck.append(v)
    deck = deck * 4
    random.shuffle(deck)

    hands = []
    for _ in range(num_players):
        hands.append(deck.pop())

    # ----- King visibility -----
    has_king = [card == 13 for card in hands]

    # ----- Turns -----
    for i in range(num_players):
        card = hands[i]

        # King holders do nothing
        if card == 13:
            continue

        # Dealer turn
        if i == num_players - 1:
            if card <= switch_threshold:
                hands[i] = deck.pop()
            continue

        # Normal player
        left = i + 1

        # Cannot swap with a King
        left = (i + 1) % num_players
        while hands[left] == 13:
            left = (left + 1) % num_players
            if left == i:
                break  # everyone else has a King

        if left != i and card <= switch_threshold:
            hands[i], hands[left] = hands[left], hands[i]


        # Decision rule
        if card <= switch_threshold:
            hands[i], hands[left] = hands[left], hands[i]

    # ----- Resolve round -----
    min_card = min(hands)
    losers = [i for i, c in enumerate(hands) if c == min_card]

    return losers
