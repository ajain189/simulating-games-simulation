import random
import matplotlib.pyplot as plt
import os
import numpy as np
from collections import Counter

# --- Configuration & Styling ---
os.makedirs("results", exist_ok=True)

# ANSI Color Codes for high-quality terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

CARD_VALUES = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
               '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13}
CARD_NAMES = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

def make_deck():
    suits = ['H', 'D', 'C', 'S']
    return [(rank, suit) for suit in suits for rank in CARD_VALUES.keys()]

def value(card):
    return CARD_VALUES[card[0]]

# --- Core Simulation Functions ---

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

# --- Enhanced Analysis & Visualization Functions ---

def run_deep_analysis(num_players=4, threshold=5, sims=100000):
    """Gathers granular data for scientific analysis."""
    losing_cards = []
    initial_cards_outcomes = {v: {'wins': 0, 'losses': 0} for v in range(1, 14)}
    final_hand_values = []
    
    for _ in range(sims):
        deck = make_deck()
        random.shuffle(deck)
        hands = [deck[i] for i in range(num_players)]
        initial_hands = [h for h in hands]
        
        # Player Turns
        for i in range(num_players):
            if hands[i][0] == 'K': continue
            if value(hands[i]) <= threshold:
                if i == num_players - 1:
                    hands[i] = deck[num_players]
                else:
                    if not (hands[i+1][0] == 'K'):
                        hands[i], hands[i+1] = hands[i+1], hands[i]
        
        final_values = [value(h) for h in hands]
        min_val = min(final_values)
        losers = [i for i, v in enumerate(final_values) if v == min_val]
        
        for i in range(num_players):
            v_initial = value(initial_hands[i])
            if i in losers:
                initial_cards_outcomes[v_initial]['losses'] += 1
                losing_cards.append(final_values[i])
            else:
                initial_cards_outcomes[v_initial]['wins'] += 1
            final_hand_values.append(final_values[i])

    return losing_cards, initial_cards_outcomes, final_hand_values

def generate_scientific_plots(losing_cards, outcomes, final_values, pos_data, thresholds):
    """Generates all required visualizations for the final deliverable."""
    fig = plt.figure(figsize=(15, 12))
    
    # 1. Optimal Thresholds
    ax1 = fig.add_subplot(2, 2, 1)
    players = list(range(3, 9))
    thresh_vals = [thresholds[n] for n in players]
    ax1.bar(players, thresh_vals, color='#3498db', edgecolor='black')
    ax1.set_title('Optimal Swap Threshold by Player Count')
    ax1.set_xlabel('Number of Players')
    ax1.set_ylabel('Swap Threshold (Value)')
    ax1.set_xticks(players)
    ax1.set_yticks(range(1, 8))
    ax1.set_yticklabels(['A', '2', '3', '4', '5', '6', '7'])

    # 2. Loss Rate by Position
    ax2 = fig.add_subplot(2, 2, 2)
    for n in [3, 4, 5, 6]:
        ax2.plot(range(n), pos_data[n], '-o', label=f'{n} players', markersize=6)
    ax2.set_title('Loss Rate by Position')
    ax2.set_xlabel('Position (last = dealer)')
    ax2.set_ylabel('Loss Rate (%)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # 3. Distribution of Losing Cards
    ax3 = fig.add_subplot(2, 2, 3)
    counts = Counter(losing_cards)
    x = range(1, 14)
    y = [counts.get(v, 0) for v in x]
    ax3.bar(x, y, color='#e74c3c', edgecolor='black', alpha=0.8)
    ax3.set_title('Final Card Values of Losers')
    ax3.set_xticks(x)
    ax3.set_xticklabels(CARD_NAMES)
    ax3.set_xlabel('Card Value')
    ax3.set_ylabel('Frequency')

    # 4. Survival Probability
    ax4 = fig.add_subplot(2, 2, 4)
    x_surv = range(1, 14)
    survival_rates = [(outcomes[v]['wins'] / (outcomes[v]['wins'] + outcomes[v]['losses']) * 100) for v in x_surv]
    ax4.plot(x_surv, survival_rates, marker='o', color='#2ecc71', linewidth=2)
    ax4.set_title('Survival Prob vs. Initial Card')
    ax4.set_xticks(x_surv)
    ax4.set_xticklabels(CARD_NAMES)
    ax4.set_xlabel('Initial Card')
    ax4.set_ylabel('Survival Rate (%)')
    ax4.set_ylim(0, 105)
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('results/scientific_analysis.png', dpi=150)
    plt.close()

# --- Main Execution Loop ---

if __name__ == "__main__":
    print(f"{Colors.HEADER}{Colors.BOLD}SCREW YOUR NEIGHBOR: SCIENTIFIC SIMULATION{Colors.ENDC}")
    print(f"{Colors.BLUE}{'='*50}{Colors.ENDC}\n")

    # 1. Optimal Threshold Analysis
    print(f"{Colors.CYAN}{Colors.BOLD}PHASE 1: STRATEGY OPTIMIZATION{Colors.ENDC}")
    print(f"{Colors.CYAN}{'-'*50}{Colors.ENDC}")
    thresholds = {}
    for n in range(3, 9):
        thresh, _, _, _ = find_optimal_threshold(n, sims=60000)
        thresholds[n] = thresh
        print(f"  {n} players: Optimal threshold is {Colors.YELLOW}{CARD_NAMES[thresh-1]}{Colors.ENDC} (value {thresh})")

    # 2. Position Advantage
    print(f"\n{Colors.CYAN}{Colors.BOLD}PHASE 2: POSITION ANALYSIS{Colors.ENDC}")
    print(f"{Colors.CYAN}{'-'*50}{Colors.ENDC}")
    position_data = {}
    for n in [3, 4, 5, 6]:
        rates = find_position_advantage(n, thresholds[n], sims=50000)
        position_data[n] = rates
        dealer_rate = rates[-1]
        others_avg = sum(rates[:-1]) / (n-1)
        diff = dealer_rate - others_avg
        color = Colors.GREEN if diff < 0 else Colors.RED
        print(f"  {n} Players: Dealer edge vs Avg: {color}{diff:+.1f}%{Colors.ENDC} (Dealer: {dealer_rate:.1f}%)")

    # 3. Deep Dive Analysis (4 Players)
    print(f"\n{Colors.CYAN}{Colors.BOLD}PHASE 3: MONTE CARLO DEEP DIVE (4 Players){Colors.ENDC}")
    print(f"{Colors.CYAN}{'-'*50}{Colors.ENDC}")
    print("  Generating granular distribution data and survival probabilities...")
    losing_cards, outcomes, final_values = run_deep_analysis(4, thresholds[4], sims=150000)
    
    # 4. Generate Visualizations
    print(f"\n{Colors.GREEN}{Colors.BOLD}PHASE 4: VISUALIZATION GENERATION{Colors.ENDC}")
    print(f"{Colors.GREEN}{'-'*50}{Colors.ENDC}")
    generate_scientific_plots(losing_cards, outcomes, final_values, position_data, thresholds)
    print(f"  [SUCCESS] All plots consolidated into {Colors.BOLD}results/scientific_analysis.png{Colors.ENDC}")
    print(f"  [SUCCESS] Detailed histograms and distributions complete.")

    print(f"\n{Colors.BLUE}{'='*50}{Colors.ENDC}")
    print(f"{Colors.BOLD}SIMULATION COMPLETE.{Colors.ENDC}\n")