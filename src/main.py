from blackjack.game import BlackjackGame, GameState

def print_game_state(game: BlackjackGame):
    status = game.get_game_status()
    print("\n" + "="*30)
    print(f"Bankroll: ${status['bankroll']}")
    print(f"Dealer Hand: {status['dealer_hand']}")
    print("Player Hands:")
    for i, hand in enumerate(status['player_hands']):
        marker = " <--" if i == game.current_hand_index and game.state == GameState.PLAYER_TURN else ""
        print(f"  Hand {i+1}: {hand}{marker}")
    print("="*30)

def main():
    print("Welcome to Blackjack Trainer!")
    player_name = input("Enter your name: ")
    game = BlackjackGame(player_name)

    while True:
        if game.player.bankroll <= 0:
            print("You're broke! Game over.")
            break
        
        try:
            bet = int(input(f"\nEnter bet amount (Current bankroll: ${game.player.bankroll}, '0' to quit): "))
            if bet == 0:
                break
            game.start_round(bet)
        except ValueError as e:
            print(f"Invalid input: {e}")
            continue

        while game.state == GameState.PLAYER_TURN:
            print_game_state(game)
            current_hand = game.player.hands[game.current_hand_index]
            
            options = ["(H)it", "(S)tand"]
            if current_hand.can_double_down():
                options.append("(D)ouble Down")
            if current_hand.can_split():
                options.append("S(P)lit")
            
            choice = input(f"Action {', '.join(options)}: ").strip().upper()

            try:
                if choice == 'H':
                    game.hit()
                elif choice == 'S':
                    game.stand()
                elif choice == 'D' and current_hand.can_double_down():
                    game.double_down()
                elif choice == 'P' and current_hand.can_split():
                    game.split()
                else:
                    print("Invalid choice.")
            except Exception as e:
                print(f"Error: {e}")

            # Display strategy feedback immediately after a move
            if game.last_move_feedback and game.last_move_feedback["hand_index"] == game.current_hand_index:
                feedback = game.last_move_feedback
                if feedback["is_correct"]:
                    print("Strategy Feedback: Correct Play!")
                else:
                    print(f"Strategy Feedback: Incorrect Play. Recommended: {feedback["recommended_move"]}")
                game.last_move_feedback = None # Clear after displaying

        print_game_state(game)

        # Display any remaining feedback for hands that finished (e.g., busted) without a specific player action
        # This might be redundant with the above, but ensures feedback for final states.
        if game.last_move_feedback:
            feedback = game.last_move_feedback
            if feedback["is_correct"]:
                print("Strategy Feedback: Correct Play!")
            else:
                print(f"Strategy Feedback: Incorrect Play. Recommended: {feedback["recommended_move"]}")
            game.last_move_feedback = None # Clear after displaying
        if game.state == GameState.ROUND_OVER:
            # Show results
            dealer_val = game.dealer.hands[0].get_value()
            dealer_bust = game.dealer.hands[0].is_bust()
            
            if dealer_bust:
                print("Dealer BUSTS!")
            else:
                print(f"Dealer stands with {dealer_val}")
            
            for i, hand in enumerate(game.player.hands):
                val = hand.get_value()
                if hand.is_bust():
                    print(f"Hand {i+1} BUSTED.")
                elif hand.is_blackjack():
                    print(f"Hand {i+1} BLACKJACK!")
                else:
                    print(f"Hand {i+1} finished with {val}")

    print(f"Final bankroll: ${game.player.bankroll}")
    print("Thanks for playing!")

if __name__ == "__main__":
    main()
