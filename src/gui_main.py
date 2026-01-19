import tkinter as tk
from tkinter import messagebox
from .blackjack.game import BlackjackGame, GameState
from .blackjack.models import Card, Hand

class BlackjackUI:
    """Manages the Blackjack GUI using tkinter."""
    
    CARD_WIDTH = 70
    CARD_HEIGHT = 100
    CARD_SPACING = 20
    
    SUIT_COLORS = {
        '♠': 'black',
        '♣': 'black',
        '♥': 'red',
        '♦': 'red'
    }

    def __init__(self, root: tk.Tk, game: BlackjackGame):
        self.root = root
        self.game = game
        self.root.title("Blackjack Trainer")
        self.root.geometry("800x600")
        
        self._setup_ui()
        self._bind_keys()
        self.update_ui()

    def _setup_ui(self):
        """Creates the main layout."""
        # Main container
        self.main_frame = tk.Frame(self.root, bg="#2e7d32") # Dark green felt color
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Dealer area
        self.dealer_frame = tk.LabelFrame(self.main_frame, text="Dealer", bg="#2e7d32", fg="white", font=("Arial", 12, "bold"))
        self.dealer_frame.pack(pady=10, fill=tk.X, padx=20)
        
        self.dealer_canvas = tk.Canvas(self.dealer_frame, height=self.CARD_HEIGHT + 20, bg="#2e7d32", highlightthickness=0)
        self.dealer_canvas.pack(fill=tk.X, padx=10, pady=5)

        # Info area (Feedback and Bankroll)
        self.info_frame = tk.Frame(self.main_frame, bg="#1b5e20")
        self.info_frame.pack(fill=tk.X, pady=5)
        
        self.status_label = tk.Label(self.info_frame, text="Welcome to Blackjack Trainer!", bg="#1b5e20", fg="white", font=("Arial", 14, "bold"), wraplength=700)
        self.status_label.pack(pady=10)
        
        self.bankroll_label = tk.Label(self.info_frame, text=f"Bankroll: ${self.game.player.bankroll}", bg="#1b5e20", fg="#ffd700", font=("Arial", 12, "bold"))
        self.bankroll_label.pack(side=tk.RIGHT, padx=20)

        # Player area
        self.player_hands_container = tk.Frame(self.main_frame, bg="#2e7d32")
        self.player_hands_container.pack(pady=10, fill=tk.BOTH, expand=True, padx=20)
        
        # We'll dynamically create canvases for player hands
        self.player_canvases = []

        # Control area
        self.controls_frame = tk.Frame(self.main_frame, bg="#1b5e20", pady=20)
        self.controls_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # Betting buttons
        self.bet_frame = tk.Frame(self.controls_frame, bg="#1b5e20")
        self.bet_10_btn = tk.Button(self.bet_frame, text="Bet $10", command=lambda: self.handle_bet(10), width=10, font=("Arial", 10, "bold"))
        self.bet_50_btn = tk.Button(self.bet_frame, text="Bet $50", command=lambda: self.handle_bet(50), width=10, font=("Arial", 10, "bold"))
        self.bet_100_btn = tk.Button(self.bet_frame, text="Bet $100", command=lambda: self.handle_bet(100), width=10, font=("Arial", 10, "bold"))
        
        self.bet_10_btn.pack(side=tk.LEFT, padx=5)
        self.bet_50_btn.pack(side=tk.LEFT, padx=5)
        self.bet_100_btn.pack(side=tk.LEFT, padx=5)

        # Action buttons
        self.action_frame = tk.Frame(self.controls_frame, bg="#1b5e20")
        self.hit_btn = tk.Button(self.action_frame, text="Hit (H)", command=self.handle_hit, width=8, font=("Arial", 10, "bold"))
        self.stand_btn = tk.Button(self.action_frame, text="Stand (S)", command=self.handle_stand, width=8, font=("Arial", 10, "bold"))
        self.double_btn = tk.Button(self.action_frame, text="Double (D)", command=self.handle_double, width=8, font=("Arial", 10, "bold"))
        self.split_btn = tk.Button(self.action_frame, text="Split (P)", command=self.handle_split, width=8, font=("Arial", 10, "bold"))
        
        self.hit_btn.pack(side=tk.LEFT, padx=5)
        self.stand_btn.pack(side=tk.LEFT, padx=5)
        self.double_btn.pack(side=tk.LEFT, padx=5)
        self.split_btn.pack(side=tk.LEFT, padx=5)

        # New round button (shown after round)
        self.new_round_btn = tk.Button(self.controls_frame, text="Next Round (Enter)", command=self._prepare_betting, width=20, font=("Arial", 12, "bold"), bg="#ffd700")

    def _bind_keys(self):
        """Binds keyboard events."""
        self.root.bind("<h>", lambda e: self.handle_hit())
        self.root.bind("<s>", lambda e: self.handle_stand())
        self.root.bind("<d>", lambda e: self.handle_double())
        self.root.bind("<p>", lambda e: self.handle_split())
        self.root.bind("<Return>", lambda e: self._handle_enter())

    def _handle_enter(self):
        """Handles the Enter key based on game state."""
        if self.game.state == GameState.BETTING:
            # Default to $10 bet if they just press Enter? Or do nothing?
            # Let's say it repeats the last bet or $10.
            self.handle_bet(10)
        elif self.game.state == GameState.ROUND_OVER:
            self._prepare_betting()

    def _prepare_betting(self):
        """Moves back to betting state."""
        self.game.state = GameState.BETTING
        self.game.last_move_feedback = None
        self.update_ui()

    def handle_bet(self, amount: int):
        """Starts a new round with the given bet."""
        try:
            self.game.start_round(amount)
            self.update_ui()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def handle_hit(self):
        """Handles hit action."""
        if self.game.state != GameState.PLAYER_TURN: return
        self.game.hit()
        self.update_ui()

    def handle_stand(self):
        """Handles stand action."""
        if self.game.state != GameState.PLAYER_TURN: return
        self.game.stand()
        self.update_ui()

    def handle_double(self):
        """Handles double down action."""
        if self.game.state != GameState.PLAYER_TURN: return
        try:
            self.game.double_down()
            self.update_ui()
        except Exception as e:
            messagebox.showwarning("Action Not Possible", str(e))

    def handle_split(self):
        """Handles split action."""
        if self.game.state != GameState.PLAYER_TURN: return
        try:
            self.game.split()
            self.update_ui()
        except Exception as e:
            messagebox.showwarning("Action Not Possible", str(e))

    def update_ui(self):
        """Refreshes the entire UI state."""
        # Update Bankroll
        self.bankroll_label.config(text=f"Bankroll: ${self.game.player.bankroll}")

        # Update Controls
        self.bet_frame.pack_forget()
        self.action_frame.pack_forget()
        self.new_round_btn.pack_forget()

        if self.game.state == GameState.BETTING:
            self.bet_frame.pack()
            self.status_label.config(text="Place your bet to start!", fg="white")
        elif self.game.state == GameState.PLAYER_TURN:
            self.action_frame.pack()
            self._show_feedback()
            # Enable/Disable Split and Double based on current hand
            curr_hand = self.game.player.hands[self.game.current_hand_index]
            self.split_btn.config(state=tk.NORMAL if curr_hand.can_split() else tk.DISABLED)
            self.double_btn.config(state=tk.NORMAL if curr_hand.can_double_down() else tk.DISABLED)
        elif self.game.state == GameState.ROUND_OVER:
            self.new_round_btn.pack()
            self._show_results()

        # Update Canvases
        self._draw_dealer_hand()
        self._draw_player_hands()

    def _show_feedback(self):
        """Displays strategy feedback for the last move."""
        feedback = self.game.last_move_feedback
        if feedback:
            move_map = {"H": "Hit", "S": "Stand", "D": "Double Down", "P": "Split"}
            rec_move = move_map.get(feedback['recommended_move'], feedback['recommended_move'])
            
            if feedback['is_correct']:
                self.status_label.config(text=f"Correct! {rec_move} was the right play.", fg="#aeea00") # Lime green
            else:
                self.status_label.config(text=f"Incorrect. You should have {rec_move}.", fg="#ff5252") # Light red
        else:
            # Show advice for the current hand if no move made yet or after a move
            advice = self.game.get_perfect_play_advice(self.game.current_hand_index)
            move_map = {"H": "Hit", "S": "Stand", "D": "Double Down", "P": "Split"}
            # self.status_label.config(text=f"Playing Hand {self.game.current_hand_index + 1}... (Psst: {move_map[advice]})", fg="white")
            self.status_label.config(text=f"Playing Hand {self.game.current_hand_index + 1}...", fg="white")

    def _show_results(self):
        """Shows the outcome of the round."""
        results = []
        dealer_val = self.game.dealer.hands[0].get_value()
        
        if self.game.dealer.hands[0].is_blackjack():
            results.append("Dealer has Blackjack!")
        elif self.game.dealer.hands[0].is_bust():
            results.append("Dealer Busted!")
        else:
            results.append(f"Dealer has {dealer_val}")

        # Summary of player hands
        for i, hand in enumerate(self.game.player.hands):
            prefix = f"Hand {i+1}: " if len(self.game.player.hands) > 1 else ""
            val = hand.get_value()
            if hand.is_blackjack():
                results.append(f"{prefix}Blackjack! Win!")
            elif hand.is_bust():
                results.append(f"{prefix}Busted!")
            elif self.game.dealer.hands[0].is_bust() or val > dealer_val:
                results.append(f"{prefix}Won with {val}!")
            elif val == dealer_val and not self.game.dealer.hands[0].is_blackjack():
                results.append(f"{prefix}Push ({val})")
            else:
                results.append(f"{prefix}Lost with {val}")

        self.status_label.config(text=" | ".join(results), fg="#ffd700")

    def _draw_card(self, canvas: tk.Canvas, card: Card, x: int, y: int, hidden: bool = False):
        """Helper to render a visual card on a canvas."""
        # Shadow/Border
        canvas.create_rectangle(x, y, x + self.CARD_WIDTH, y + self.CARD_HEIGHT, fill="white", outline="black", width=2)
        
        if hidden:
            # Draw card back
            canvas.create_rectangle(x + 5, y + 5, x + self.CARD_WIDTH - 5, y + self.CARD_HEIGHT - 5, fill="#1565c0", outline="#0d47a1")
            canvas.create_text(x + self.CARD_WIDTH//2, y + self.CARD_HEIGHT//2, text="?", fill="white", font=("Arial", 20, "bold"))
            return

        color = self.SUIT_COLORS.get(card.suit, "black")
        
        # Rank and Suit in top-left
        canvas.create_text(x + 5, y + 5, text=card.rank, anchor=tk.NW, fill=color, font=("Arial", 12, "bold"))
        canvas.create_text(x + 5, y + 22, text=card.suit, anchor=tk.NW, fill=color, font=("Arial", 14))
        
        # Suit in center
        canvas.create_text(x + self.CARD_WIDTH//2, y + self.CARD_HEIGHT//2, text=card.suit, fill=color, font=("Arial", 30))
        
        # Rank and Suit in bottom-right (rotated-like)
        canvas.create_text(x + self.CARD_WIDTH - 5, y + self.CARD_HEIGHT - 5, text=card.rank, anchor=tk.SE, fill=color, font=("Arial", 12, "bold"))
        canvas.create_text(x + self.CARD_WIDTH - 5, y - 22 + self.CARD_HEIGHT, text=card.suit, anchor=tk.SE, fill=color, font=("Arial", 14))

    def _draw_dealer_hand(self):
        """Renders the dealer's cards."""
        self.dealer_canvas.delete("all")
        if self.game.state == GameState.BETTING:
            return
            
        hand = self.game.dealer.hands[0]
        hide_first = (self.game.state == GameState.PLAYER_TURN)
        
        for i, card in enumerate(hand.cards):
            is_hidden = (i == 1 and hide_first)
            # Adjusted card spacing for dealer
            self._draw_card(self.dealer_canvas, card, 10 + i * (self.CARD_WIDTH // 2 + 10), 10, hidden=is_hidden)
            
        if not hide_first:
            val = hand.get_value()
            # Adjust value label position if cards are spread out more
            self.dealer_canvas.create_text(10, self.CARD_HEIGHT + 15, text=f"Value: {val}", anchor=tk.W, fill="white", font=("Arial", 10, "bold"))

    def _draw_player_hands(self):
        """Renders the player's hands (supports multiple for splits)."""
        # Clear existing canvases and their parent frames to prevent cumulative packing issues
        for widget in self.player_hands_container.winfo_children():
            widget.destroy()
        self.player_canvases = []

        if self.game.state == GameState.BETTING:
            return

        # Use grid for player hands to allow for multiple rows if needed, or better horizontal control
        # For now, we'll keep it in a row, but control spacing better.
        for i, hand in enumerate(self.game.player.hands):
            # Create a sub-frame for each hand to contain its label and canvas
            hand_frame = tk.Frame(self.player_hands_container, bg="#2e7d32")
            hand_frame.grid(row=0, column=i, padx=10, pady=5)
            
            # Highlight current hand
            bg_color = "#388e3c" if i == self.game.current_hand_index and self.game.state == GameState.PLAYER_TURN else "#2e7d32"
            title = f"Hand {i+1}" if len(self.game.player.hands) > 1 else "Your Hand"
            if hand.bet:
                title += f" (${hand.bet})"
            
            label = tk.Label(hand_frame, text=title, bg=bg_color, fg="white", font=("Arial", 10, "bold"))
            label.pack(pady=(0, 5))
            
            # Calculate canvas width based on maximum expected cards (e.g., 5 cards slightly overlapping)
            canvas_width = self.CARD_WIDTH + (5 * (self.CARD_WIDTH // 3)) # Accommodate up to 5 cards with overlap
            canvas = tk.Canvas(hand_frame, width=canvas_width, height=self.CARD_HEIGHT + 40, bg=bg_color, highlightthickness=1 if i == self.game.current_hand_index and self.game.state == GameState.PLAYER_TURN else 0, highlightbackground="yellow")
            canvas.pack()
            self.player_canvases.append(canvas)
            
            for j, card in enumerate(hand.cards):
                # Adjusted card spacing for player hands to create overlapping effect
                self._draw_card(canvas, card, 10 + j * (self.CARD_WIDTH // 3), 10) # Cards overlap by 2/3 of their width
            
            val = hand.get_value()
            status = ""
            if hand.is_blackjack(): status = " - BLACKJACK!"
            elif hand.is_bust(): status = " - BUST!"
            elif hand.is_stayed: status = " - Stayed"
            
            canvas.create_text(10, self.CARD_HEIGHT + 25, text=f"Value: {val}{status}", anchor=tk.W, fill="white", font=("Arial", 10, "bold"))

if __name__ == "__main__":
    root = tk.Tk()
    game = BlackjackGame("Player")
    ui = BlackjackUI(root, game)
    root.mainloop()
