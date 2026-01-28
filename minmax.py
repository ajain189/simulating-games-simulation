import random
import matplotlib.pyplot as plt
import os

os.makedirs("results", exist_ok=True)

CARD_VALUES = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
               '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13}
CARD_NAMES = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

def make_deck():
    suits = ['H', 'D', 'C', 'S']
    return [(rank, suit) for suit in suits for rank in CARD_VALUES.keys()]

def value(card):
    return CARD_VALUES[card[0]]

def play_round(num_players, threshold):
    deck = make_deck()
    random.shuffle(deck)
    
    hands = [deck[i] for i in range(num_players)]
    kings_shown = [hands[i][0] == 'K' for i in range(num_players)]
    
    for i in range(num_players):
        if hands[i][0] == 'K':
            continue
        
        should_swap = value(hands[i]) <= threshold
        if not should_swap:
            continue
        
        if i == num_players - 1:
            hands[i] = deck[num_players]
        else:
            left = (i + 1) % num_players
            if not kings_shown[left]:
                hands[i], hands[left] = hands[left], hands[i]
                if hands[i][0] == 'K':
                    kings_shown[i] = True
                if hands[left][0] == 'K':
                    kings_shown[left] = True
    
    values = [value(h) for h in hands]
    min_val = min(values)
    losers = [i for i in range(num_players) if values[i] == min_val]
    return losers

def find_position_advantage(num_players, threshold, sims=50000):
    losses = [0] * num_players
    for _ in range(sims):
        for loser in play_round(num_players, threshold):
            losses[loser] += 1
    return [losses[i] / sims * 100 for i in range(num_players)]

def find_optimal_threshold(num_players, sims=80000):
    keep_survive = {v: 0 for v in range(1, 13)}
    swap_survive = {v: 0 for v in range(1, 13)}
    counts = {v: 0 for v in range(1, 13)}
    
    for _ in range(sims):
        deck = make_deck()
        random.shuffle(deck)
        hands = [deck[i] for i in range(num_players)]
        
        my_val = value(hands[0])
        if my_val == 13:
            continue
        
        counts[my_val] += 1
        
        min_val = min(value(h) for h in hands)
        if my_val > min_val:
            keep_survive[my_val] += 1
        
        if hands[1][0] != 'K':
            swapped = hands.copy()
            swapped[0], swapped[1] = swapped[1], swapped[0]
            new_min = min(value(h) for h in swapped)
            if value(swapped[0]) > new_min:
                swap_survive[my_val] += 1
    
    threshold = 0
    for v in range(1, 13):
        if counts[v] == 0:
            continue
        keep_rate = keep_survive[v] / counts[v] * 100
        swap_rate = swap_survive[v] / counts[v] * 100
        if swap_rate > keep_rate:
            threshold = v
    
    return threshold, keep_survive, swap_survive, counts


print("SCREW YOUR NEIGHBOR SIMULATION")
print("=" * 50)
print()

print("OPTIMAL SWAP THRESHOLD BY NUMBER OF PLAYERS")
print("-" * 50)
print("(Swap if your card is at or below this value)")
print()

thresholds = {}
for n in range(3, 9):
    thresh, keep, swap, counts = find_optimal_threshold(n, sims=60000)
    thresholds[n] = thresh
    print(f"{n} players: Swap if card <= {CARD_NAMES[thresh-1]} (value {thresh})")

print()
print("In other words:")
for n in range(3, 9):
    t = thresholds[n]
    print(f"  {n} players: SWAP with {CARD_NAMES[:t]}, KEEP with {CARD_NAMES[t:]}")

print()
print()
print("POSITION ADVANTAGE")
print("-" * 50)
print("(Using optimal threshold for each player count)")
print()

position_data = {}
for n in [3, 4, 5, 6]:
    rates = find_position_advantage(n, thresholds[n], sims=50000)
    position_data[n] = rates
    expected = 100 / n
    
    print(f"{n} Players:")
    for pos in range(n):
        diff = rates[pos] - expected
        sign = "+" if diff > 0 else ""
        role = " (dealer)" if pos == n-1 else ""
        print(f"  Position {pos}{role}: {rates[pos]:.1f}% loss rate ({sign}{diff:.1f}%)")
    print()

print()
print("DEALER VS NON-DEALER")
print("-" * 50)
for n in [4, 5, 6]:
    rates = position_data[n]
    dealer = rates[n-1]
    others = sum(rates[:-1]) / (n-1)
    diff = dealer - others
    sign = "+" if diff > 0 else ""
    print(f"{n} players: Dealer {dealer:.1f}%, Others avg {others:.1f}% ({sign}{diff:.1f}%)")

print()
print()
print("DETAILED SWAP VS KEEP (5 Players)")
print("-" * 50)
thresh, keep, swap, counts = find_optimal_threshold(5, sims=100000)
print(f"{'Card':<6}{'Keep %':<12}{'Swap %':<12}{'Better'}")
for v in range(1, 13):
    if counts[v] == 0:
        continue
    k = keep[v] / counts[v] * 100
    s = swap[v] / counts[v] * 100
    better = "SWAP" if s > k else "KEEP"
    print(f"{CARD_NAMES[v-1]:<6}{k:<12.1f}{s:<12.1f}{better}")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

players = list(range(3, 9))
thresh_vals = [thresholds[n] for n in players]
ax1.bar(players, thresh_vals, color='#3498db', edgecolor='black')
ax1.set_xlabel('Number of Players')
ax1.set_ylabel('Swap Threshold (card value)')
ax1.set_title('Optimal Swap Threshold by Player Count')
ax1.set_xticks(players)
ax1.set_yticks(range(1, 8))
ax1.set_yticklabels(['A', '2', '3', '4', '5', '6', '7'])

for n in [3, 4, 5, 6]:
    ax2.plot(range(n), position_data[n], '-o', label=f'{n} players', markersize=6)
ax2.set_xlabel('Position (last = dealer)')
ax2.set_ylabel('Loss Rate (%)')
ax2.set_title('Loss Rate by Position')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('results/simulation_results.png', dpi=150)
plt.close()

print()
print()
print("Graph saved to results/simulation_results.png")