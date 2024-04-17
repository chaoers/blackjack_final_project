import random
import numpy as np
import matplotlib.pyplot as plt

class Card:
    def __init__(self, rank):
        self.rank = rank

    def __str__(self):
        return f"{self.rank}"

class Deck:
    def __init__(self):
        self.cards = []
        ranks = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]
        for rank in ranks:
            self.cards.append(Card(rank))
        self.cards *= 4

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        if len(self.cards) > 0:
            return self.cards.pop()

class Shoe:
    def __init__(self):
        self.cards = []
        for _ in range(8):
            deck = Deck()
            self.cards.extend(deck.cards)
        cut_card_position = random.randint(len(self.cards) // 2, len(self.cards))
        self.cards.insert(cut_card_position, "Cut Card")

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        if len(self.cards) > 0:
            card = self.cards.pop()
            # shuffle and reinsert cut card if it's drawn, deal another card from the shuffled shoe
            if card == "Cut Card":
                self.cards = []
                for _ in range(8):
                    deck = Deck()
                    self.cards.extend(deck.cards)
                cut_card_position = random.randint(len(self.cards) // 2, len(self.cards))
                self.cards.insert(cut_card_position, "Cut Card")
                self.shuffle()
                return self.deal()
            else:
                return card

class Hand:
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def get_value(self):
        value = 0
        num_aces = 0
        for card in self.cards:
            if card.rank == "Ace":
                num_aces += 1
            elif card.rank in ["Jack", "Queen", "King"]:
                value += 10
            else:
                value += int(card.rank)

        for _ in range(num_aces):
            if value + 11 <= 21:
                value += 11
            else:
                value += 1

        return value

    def __str__(self):
        return ", ".join(str(card) for card in self.cards)


class Dealer:
    def __init__(self):
        self.hand = Hand()

    def play(self, shoe):
        while self.hand.get_value() < 17:
            self.hand.add_card(shoe.deal())

class QLearningPlayer:
    def __init__(self, learning_rate, discount_factor, exploration_rate):
        self.q_table = {}
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate

    def get_state(self, player_hand, dealer_upcard):
        return (player_hand, dealer_upcard.rank)

    def get_action(self, state, valid_actions):
        # epsilon-greedy
        if np.random.uniform(0, 1) < self.exploration_rate:
            return random.choice(valid_actions)
        else:
            if state not in self.q_table:
                self.q_table[state] = {action: 0 for action in valid_actions}
            return max(self.q_table[state], key=self.q_table[state].get)

    def update_q_table(self, state, action, reward, next_state):
        player_hand, dealer_upcard = state
        player_hand_value = player_hand.get_value()
        
        # if seeing the state for the first time, add it and its valid actions to the q-table
        if (player_hand_value, dealer_upcard) not in self.q_table:
            self.q_table[(player_hand_value, dealer_upcard)] = {a: 0 for a in get_valid_actions(player_hand)}
        
        # Retrieve the Q-value for the given action at the current state
        old_value = self.q_table[(player_hand_value, dealer_upcard)].get(action, 0)
        # Default value if there is no next state
        next_max = 0
        
        # get the maximum Q-value for the next state across all possible actions if it exists
        if next_state is not None:
            next_player_hand, next_dealer_upcard = next_state
            next_player_hand_value = next_player_hand.get_value()
            if (next_player_hand_value, next_dealer_upcard) in self.q_table:
                next_max = max(self.q_table[(next_player_hand_value, next_dealer_upcard)].values())
        
        # update q value using the formula
        new_value = old_value + self.learning_rate * (reward + self.discount_factor * next_max - old_value)
        self.q_table[(player_hand_value, dealer_upcard)][action] = new_value

def get_valid_actions(player_hand):
    actions = ["hit", "stay"]
    if len(player_hand.cards) == 2:
        if player_hand.cards[0].rank == player_hand.cards[1].rank:
            actions.append("split")
        actions.append("double")
    return actions

def simulate_game(num_rounds, decay_rate):
    shoe = Shoe()
    shoe.shuffle()

    player = QLearningPlayer(learning_rate=0.1, discount_factor=0.9, exploration_rate=1)
    dealer = Dealer()

    results = []
    win_rates = []
    graph_interval=1000

    for round_num in range(num_rounds):
        player_hands = [Hand()]
        dealer_hand = Hand()

        # Deal initial cards
        player_hands[0].add_card(shoe.deal())
        dealer_hand.add_card(shoe.deal())
        player_hands[0].add_card(shoe.deal())
        dealer_hand.add_card(shoe.deal())

        # Check for player's blackjack
        if player_hands[0].get_value() == 21:
            if dealer_hand.get_value() != 21:
                results.append("win")
            else:
                results.append("draw")
            continue

        # Start of the player's turn, iterating over each hand the player might have (accounting for splits)
        hand_index = 0
        while hand_index < len(player_hands):
            # Current hand being played
            player_hand = player_hands[hand_index]
            state = player.get_state(player_hand, dealer_hand.cards[0])
            valid_actions = get_valid_actions(player_hand)

            while True:
                action = player.get_action(state, valid_actions)

                if action == "hit":
                    player_hand.add_card(shoe.deal())
                    next_state = player.get_state(player_hand, dealer_hand.cards[0])
                    reward = 0
                    if player_hand.get_value() > 21:
                        reward = -1
                        player.update_q_table(state, action, reward, None)
                        break
                    valid_actions = get_valid_actions(player_hand)
                    player.update_q_table(state, action, reward, next_state)
                    state = next_state
                elif action == "split":
                    if len(player_hand.cards) == 2 and player_hand.cards[0].rank == player_hand.cards[1].rank:
                        split_hand = Hand()
                        split_hand.add_card(player_hand.cards.pop())
                        player_hands.insert(hand_index + 1, split_hand)
                        player_hand.add_card(shoe.deal())
                        split_hand.add_card(shoe.deal())
                        break
                else:  
                    if action == "double":
                        player_hand.add_card(shoe.deal())
                        if player_hand.get_value() > 21:
                            reward = -1
                            player.update_q_table(state, action, reward, None)
                    break
            # Move to the next hand
            hand_index += 1

        # Dealer's turn
        dealer.play(shoe)

        # Determine winner
        for player_hand in player_hands:
            player_value = player_hand.get_value()
            dealer_value = dealer_hand.get_value()

            if player_value > 21:
                result = "loss"
            elif dealer_value > 21:
                result = "win"
            elif player_value > dealer_value:
                result = "win"
            elif dealer_value > player_value:
                result = "loss"
            else:
                result = "draw"

            results.append(result)

            if result == "win":
                reward = 10
            elif result == "draw":
                reward = 1
            else:
                reward = -10
            player.update_q_table(state, action, reward, player.get_state(player_hand, dealer_hand.cards[0]))

        if (round_num + 1) % graph_interval == 0:
            recent_results = results[-graph_interval:]
            win_rate = recent_results.count("win") / len(recent_results)
            win_rates.append((round_num + 1, win_rate))

        player.exploration_rate = max(0.001, player.exploration_rate * decay_rate)

    return results, player.q_table, win_rates

# function for creating win/loss/draw histogram
def plot_results(results, fname, decay_rate):
    plt.figure(figsize=(10, 6))
    counts = [results.count("win"), results.count("loss"), results.count("draw")]
    bars = plt.bar(["Win", "Loss", "Draw"], counts)
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height,
                 str(height), ha='center', va='bottom')
    
    plt.title("Simulation Results, decay rate "+str(decay_rate))
    plt.xlabel("Result")
    plt.ylabel("Count")
    plt.savefig(fname, dpi=300, bbox_inches='tight')
    plt.close()

# function for mapping win rate over the learning process
def plot_learning_progress(win_rates, fname, decay_rate):
    iterations, win_rates = zip(*win_rates)
    plt.figure(figsize=(10, 6))
    plt.plot(iterations, win_rates)
    plt.title("Learning Progress, decay rate "+str(decay_rate))
    plt.xlabel("Iteration")
    plt.ylabel("Win Rate")
    plt.savefig(fname, dpi=300, bbox_inches='tight')
    plt.close()

# function for printing out learned strategy
def print_optimal_strategy(q_table, iteration):
    player_hands = ["4", "5", "6", "7", "8", "9", "10", "11", "12", "13", 
                    "14", "15", "16", "17", "18", "19", "20", "21"]
    dealer_upcards = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]
    
    strategy_table = np.empty((len(player_hands), len(dealer_upcards)), dtype=object)
    
    for i, player_hand in enumerate(player_hands):
        for j, dealer_upcard in enumerate(dealer_upcards):
            state = (int(player_hand) if player_hand.isdigit() else player_hand, dealer_upcard)
            if state in q_table:
                if all(value == 0 for value in q_table[state].values()):
                    strategy_table[i, j] = "stay"  # Choose "stay" as the best action if all values are 0
                else:
                    best_action = max(q_table[state], key=q_table[state].get)
                    strategy_table[i, j] = best_action
            else:
                strategy_table[i, j] = ""
    
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.axis('tight')
    ax.axis('off')
    table = ax.table(cellText=strategy_table, colLabels=dealer_upcards, rowLabels=player_hands, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.2, 1.2)
    
    plt.title("Optimal Strategy "+str(iteration)+" iterations")
    plt.savefig(str(iteration)+"optimal_strategy.png", dpi=300, bbox_inches='tight')
    plt.close()

def main():
    num_rounds = 10000000
    decay_rate = 0.9999999999999999
    results, q_table, win_rates = simulate_game(num_rounds, decay_rate)
    
    print(q_table)
    plot_results(results, str(num_rounds)+" round result", decay_rate)
    plot_learning_progress(win_rates, str(num_rounds)+"winrate", decay_rate)
    print_optimal_strategy(q_table, num_rounds)

if __name__ == "__main__":
    main()