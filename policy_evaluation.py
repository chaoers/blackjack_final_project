from blackjack import Shoe, Dealer, Hand

class FixedStrategyPlayer:
    def __init__(self):
        pass

    def get_action(self, player_hand, dealer_upcard):
        return self.basic_strategy(player_hand, dealer_upcard)

    def basic_strategy(self, player_hand, dealer_upcard):
        player_value = player_hand.get_value()
        dealer_rank = dealer_upcard.rank if dealer_upcard.rank not in ['Jack', 'Queen', 'King'] else '10'
        dealer_value = 11 if dealer_rank == 'Ace' else int(dealer_rank)

        # Handle pairs (splitting)
        if len(player_hand.cards) == 2 and player_hand.cards[0].rank == player_hand.cards[1].rank:
            pair_rank = player_hand.cards[0].rank
            if pair_rank in ['Ace', '8']:  
                return 'split'
            elif pair_rank == '10' or pair_rank == 'Jack' or pair_rank == 'Queen' or pair_rank == 'King':  
                return 'stay'
            elif pair_rank == '9' and dealer_value not in [7, 10, 11]:
                return 'split'
            elif pair_rank == '7' and dealer_value < 8:
                return 'split'
            elif pair_rank == '6' and dealer_value < 7:
                return 'split'
            elif pair_rank == '4' and dealer_value in [5, 6]:
                return 'split'
            elif pair_rank == '3' or pair_rank == '2' and dealer_value < 8:
                return 'split'

        # Decisions for soft hands 
        if 'Ace' in [card.rank for card in player_hand.cards]:
            if player_value in range(19, 22):
                return 'stay'
            elif player_value == 18:
                if dealer_value in [2, 7, 8]:
                    return 'stay'
                elif dealer_value in [3, 4, 5, 6]:
                    return 'double' if len(player_hand.cards) == 2 else 'stay'
                else:
                    return 'hit'
            elif player_value in [16, 17]:
                return 'double' if dealer_value in [3, 4, 5, 6] else 'hit'
            elif player_value == 15:
                return 'double' if dealer_value in [4, 5, 6] else 'hit'
            elif player_value in [13, 14]:
                return 'double' if dealer_value in [5, 6] else 'hit'

        # Decisions for hard hands
        if player_value >= 17:
            return 'stay'
        elif player_value in [13, 14, 15, 16]:
            if dealer_value < 7:
                return 'stay'
            else:
                return 'hit'
        elif player_value == 12:
            if dealer_value in [4, 5, 6]:
                return 'stay'
            else:
                return 'hit'
        elif player_value in [10, 11]:
            if dealer_value < player_value or dealer_value > 11:
                return 'double'
            else:
                return 'hit'
        elif player_value == 9:
            return 'double' if dealer_value in [3, 4, 5, 6] else 'hit'
        elif player_value < 9:
            return 'hit'

        return 'hit'  # Default action

def simulate_game(num_rounds):
    shoe = Shoe()  # Create a shoe of cards
    shoe.shuffle()  # Shuffle the shoe

    player = FixedStrategyPlayer()  
    dealer = Dealer()  

    results = []  # List to store the results of each game ('win', 'loss', 'draw')

    for _ in range(num_rounds):
        player_hands = [Hand()]  # Initialize with one hand for the player
        dealer_hand = Hand()  # Create a new hand for the dealer

        # Initial deal: two cards each
        player_hands[0].add_card(shoe.deal())
        player_hands[0].add_card(shoe.deal())
        dealer_hand.add_card(shoe.deal())
        dealer_hand.add_card(shoe.deal())

        # Process each hand potentially created from splits
        hand_index = 0
        while hand_index < len(player_hands):
            current_hand = player_hands[hand_index]
            player_done = False
            while not player_done:
                action = player.get_action(current_hand, dealer_hand.cards[0])
                if action == 'hit':
                    current_hand.add_card(shoe.deal())
                    if current_hand.get_value() > 21:  
                        player_done = True
                elif action == 'double':
                    current_hand.add_card(shoe.deal())
                    player_done = True
                elif action == 'split':
                    # Only split if there are exactly two cards of the same rank
                    if len(current_hand.cards) == 2 and current_hand.cards[0].rank == current_hand.cards[1].rank:
                        new_hand = Hand()
                        new_hand.add_card(current_hand.cards.pop())  # Move one card to the new hand
                        current_hand.add_card(shoe.deal())  # Draw new card for the current hand
                        new_hand.add_card(shoe.deal())  # Draw new card for the new hand
                        player_hands.append(new_hand)  # Add the new hand to the list of player's hands
                else:  # 'stay'
                    player_done = True
            hand_index += 1

        # Dealer's turn
        dealer.play(shoe)

        # Determine the outcome for each hand
        for hand in player_hands:
            player_value = hand.get_value()
            dealer_value = dealer_hand.get_value()
            if player_value > 21:
                results.append('loss')
            elif dealer_value > 21 or player_value > dealer_value:
                results.append('win')
            elif player_value == dealer_value:
                results.append('draw')
            else:
                results.append('loss')

    return results


def analyze_results(results):
    wins = results.count('win')
    losses = results.count('loss')
    draws = results.count('draw')
    total_games = len(results)
    print("Results after", total_games, "rounds:")
    print("Wins:", wins, "(", wins / total_games * 100, "%)")
    print("Losses:", losses, "(", losses / total_games * 100, "%)")
    print("Draws:", draws, "(", draws / total_games * 100, "%)")

def main():
    num_rounds = 50000000
    results = simulate_game(num_rounds)
    analyze_results(results)

if __name__ == "__main__":
    main()
