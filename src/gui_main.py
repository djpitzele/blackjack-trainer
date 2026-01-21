import tkinter as tk
from tkinter import messagebox, simpledialog
from blackjack.game import BlackjackGame, GameState
from blackjack.models import Card, Hand

COUNT_MIN = 1
COUNT_MAX = 3

class BlackjackUI:
    """Manages the Blackjack GUI using tkinter."""
    
    CARD_SCALE_FACTOR = 2.0
    CARD_WIDTH = int(70 * CARD_SCALE_FACTOR)
    CARD_HEIGHT = int(100 * CARD_SCALE_FACTOR)
    CARD_SPACING = int(20 * CARD_SCALE_FACTOR)
    
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
        
        self.dealer_canvas = tk.Canvas(self.dealer_frame, height=self.CARD_HEIGHT + int(40 * self.CARD_SCALE_FACTOR), bg="#2e7d32", highlightthickness=0)
        self.dealer_canvas.pack(fill=tk.X, padx=10, pady=5)

        # Info area (Feedback and Bankroll)
        self.info_frame = tk.Frame(self.main_frame, bg="#1b5e20")
        self.info_frame.pack(fill=tk.X, pady=5)
        
        self.status_label = tk.Label(self.info_frame, text="Welcome to Blackjack Trainer!", bg="#1b5e20", fg="white", font=("Arial", 18, "bold"), wraplength=700)
        self.status_label.pack(pady=20)

        # Player area
        self.player_hands_container = tk.Frame(self.main_frame, bg="#2e7d32")
        self.player_hands_container.pack(pady=10, fill=tk.BOTH, expand=True, padx=20)
        self.player_hands_container.grid_rowconfigure(0, weight=1)
        
        # We'll dynamically create canvases for player hands
        self.player_canvases = []

        # Control area
        self.controls_frame = tk.Frame(self.main_frame, bg="#1b5e20", pady=10)
        self.controls_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # Result display (less central)
        self.results_label = tk.Label(self.controls_frame, text="", bg="#1b5e20", fg="#ffd700", font=("Arial", 11, "italic"))
        self.results_label.pack(pady=5)

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

        # New round button (shown after round or at start)
        self.new_round_btn = tk.Button(self.controls_frame, text="Deal Hand (Enter)", command=self._start_new_round, width=20, font=("Arial", 12, "bold"), bg="#ffd700")

    def _bind_keys(self):
        """Binds keyboard events."""
        self.root.bind("<h>", lambda e: self.handle_hit())
        self.root.bind("<s>", lambda e: self.handle_stand())
        self.root.bind("<d>", lambda e: self.handle_double())
        self.root.bind("<p>", lambda e: self.handle_split())
        self.root.bind("<Return>", lambda e: self._handle_enter())

    def _handle_enter(self):
        """Handles the Enter key based on game state."""
        if self.game.state == GameState.ROUND_OVER:
            self._start_new_round()

    def _start_new_round(self):
        """Starts a new round."""
        try:
            self.game.start_round()
            self.update_ui()
            if self.game.state == GameState.ROUND_OVER:
                self._check_count_query()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def handle_hit(self):
        """Handles hit action."""
        if self.game.state != GameState.PLAYER_TURN: return
        self.game.hit()
        self._check_state_and_update()

    def handle_stand(self):
        """Handles stand action."""
        if self.game.state != GameState.PLAYER_TURN: return
        self.game.stand()
        self._check_state_and_update()

    def handle_double(self):
        """Handles double down action."""
        if self.game.state != GameState.PLAYER_TURN: return
        try:
            self.game.double_down()
            self._check_state_and_update()
        except Exception as e:
            messagebox.showwarning("Action Not Possible", str(e))

    def handle_split(self):
        """Handles split action."""
        if self.game.state != GameState.PLAYER_TURN: return
        try:
            self.game.split()
            self._check_state_and_update()
        except Exception as e:
            messagebox.showwarning("Action Not Possible", str(e))

    def _check_state_and_update(self):
        """Checks if it's the dealer's turn and updates the UI."""
        self.update_ui()
        if self.game.state == GameState.DEALER_TURN:
            self.root.after(750, self._process_dealer_turn)

    def _process_dealer_turn(self):
        """Handles the dealer's turn with delays."""
        if self.game.state != GameState.DEALER_TURN:
            return

        hit = self.game.dealer_hit_if_needed()
        self.update_ui()
        
        if hit:
            self.root.after(750, self._process_dealer_turn)
        else:
            self.game.resolve_round()
            self.update_ui()
            self._check_count_query()

    def _check_count_query(self):
        """Prompts the user for the count if needed."""
        if self.game.needs_count_verification:
            user_count = simpledialog.askinteger("Card Counting", "What is the current running count?", parent=self.root)
            
            actual_count = self.game.running_count
            if user_count == actual_count:
                messagebox.showinfo("Correct!", f"Well done! The running count is indeed {actual_count}.")
            else:
                messagebox.showerror("Incorrect", f"The correct running count was {actual_count}.")
            
            # Reset the query state in the game
            self.game.needs_count_verification = False
            import random
            self.game.hands_until_next_query = random.randint(COUNT_MIN, COUNT_MAX)

    def update_ui(self):
        """Refreshes the entire UI state."""
        # Update Controls
        self.action_frame.pack_forget()
        self.new_round_btn.pack_forget()
        self.results_label.config(text="") # Clear results by default

        if self.game.state == GameState.PLAYER_TURN:
            self.action_frame.pack()
            self._show_feedback()
            # Enable/Disable Split and Double based on current hand
            curr_hand = self.game.player.hands[self.game.current_hand_index]
            self.split_btn.config(state=tk.NORMAL if curr_hand.can_split() else tk.DISABLED)
            self.double_btn.config(state=tk.NORMAL if curr_hand.can_double_down() else tk.DISABLED)
        elif self.game.state == GameState.ROUND_OVER:
            self.new_round_btn.pack()
            if self.game.dealer.hands[0].cards:
                self._show_results()
                self._show_feedback() # Show final feedback even when round is over
            else:
                self.status_label.config(text="Welcome to Blackjack Trainer!", fg="white")

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
            if self.game.state == GameState.PLAYER_TURN:
                # Show advice for the current hand if no move made yet or after a move
                advice = self.game.get_perfect_play_advice(self.game.current_hand_index)
                move_map = {"H": "Hit", "S": "Stand", "D": "Double Down", "P": "Split"}
                self.status_label.config(text=f"Hand {self.game.current_hand_index + 1}: What's the best move?", fg="white")
            elif self.game.state == GameState.ROUND_OVER and not self.game.last_move_feedback:
                 self.status_label.config(text="Round Complete", fg="white")

    def _show_results(self):
        """Shows the outcome of the round."""
        results = []
        dealer_val = self.game.dealer.hands[0].get_value()
        
        if self.game.dealer.hands[0].is_blackjack():
            results.append("Dealer: Blackjack")
        elif self.game.dealer.hands[0].is_bust():
            results.append("Dealer: Busted")
        else:
            results.append(f"Dealer: {dealer_val}")

        # Summary of player hands
        for i, hand in enumerate(self.game.player.hands):
            prefix = f"Hand {i+1}: " if len(self.game.player.hands) > 1 else "You: "
            val = hand.get_value()
            if hand.is_blackjack():
                results.append(f"{prefix}Blackjack")
            elif hand.is_bust():
                results.append(f"{prefix}Bust")
            elif self.game.dealer.hands[0].is_bust() or val > dealer_val:
                results.append(f"{prefix}Win ({val})")
            elif val == dealer_val and not self.game.dealer.hands[0].is_blackjack():
                results.append(f"{prefix}Push ({val})")
            else:
                results.append(f"{prefix}Loss ({val})")

        self.results_label.config(text=" | ".join(results))

    def _draw_card(self, canvas: tk.Canvas, card: Card, x: int, y: int, hidden: bool = False):
        """Helper to render a visual card on a canvas."""
        # Shadow/Border
        canvas.create_rectangle(x, y, x + self.CARD_WIDTH, y + self.CARD_HEIGHT, fill="white", outline="black", width=2)
        
        if hidden:
            # Draw card back
            canvas.create_rectangle(x + int(5 * self.CARD_SCALE_FACTOR), y + int(5 * self.CARD_SCALE_FACTOR),
                                    x + self.CARD_WIDTH - int(5 * self.CARD_SCALE_FACTOR),
                                    y + self.CARD_HEIGHT - int(5 * self.CARD_SCALE_FACTOR),
                                    fill="#1565c0", outline="#0d47a1")
            canvas.create_text(x + self.CARD_WIDTH//2, y + self.CARD_HEIGHT//2, text="?", fill="white",
                               font=("Arial", int(20 * self.CARD_SCALE_FACTOR), "bold"))
            return

        color = self.SUIT_COLORS.get(card.suit, "black")

        # Rank and Suit in top-left
        canvas.create_text(x + int(5 * self.CARD_SCALE_FACTOR), y + int(5 * self.CARD_SCALE_FACTOR), text=card.rank,
                           anchor=tk.NW, fill=color, font=("Arial", int(12 * self.CARD_SCALE_FACTOR), "bold"))
        canvas.create_text(x + int(5 * self.CARD_SCALE_FACTOR), y + int(22 * self.CARD_SCALE_FACTOR), text=card.suit,
                           anchor=tk.NW, fill=color, font=("Arial", int(14 * self.CARD_SCALE_FACTOR)))

        # Suit in center
        canvas.create_text(x + self.CARD_WIDTH//2, y + self.CARD_HEIGHT//2, text=card.suit, fill=color,
                           font=("Arial", int(30 * self.CARD_SCALE_FACTOR)))

        # Rank and Suit in bottom-right (rotated-like)
        canvas.create_text(x + self.CARD_WIDTH - int(5 * self.CARD_SCALE_FACTOR),
                           y + self.CARD_HEIGHT - int(5 * self.CARD_SCALE_FACTOR),
                           text=card.rank, anchor=tk.SE, fill=color,
                           font=("Arial", int(12 * self.CARD_SCALE_FACTOR), "bold"))
        canvas.create_text(x + self.CARD_WIDTH - int(5 * self.CARD_SCALE_FACTOR),
                           y - int(22 * self.CARD_SCALE_FACTOR) + self.CARD_HEIGHT,
                           text=card.suit, anchor=tk.SE, fill=color,
                           font=("Arial", int(14 * self.CARD_SCALE_FACTOR)))

    def _draw_dealer_hand(self):
        """Renders the dealer's cards."""
        self.dealer_canvas.delete("all")
        if not self.game.dealer.hands[0].cards:
            return
            
        hand = self.game.dealer.hands[0]
        hide_first = (self.game.state == GameState.PLAYER_TURN)
        
        for i, card in enumerate(hand.cards):
            is_hidden = (i == 1 and hide_first)
            # Adjusted card spacing for dealer
            card_overlap_x = int(self.CARD_WIDTH * 0.4) # Overlap by 40% for visual appeal
            total_hand_width = self.CARD_WIDTH + (len(hand.cards) - 1) * card_overlap_x
            
            canvas_center_x = self.dealer_canvas.winfo_width() / 2
            start_x = canvas_center_x - (total_hand_width / 2)

            self._draw_card(self.dealer_canvas, card, start_x + i * card_overlap_x, int(10 * self.CARD_SCALE_FACTOR), hidden=is_hidden)
            
        # if not hide_first:
            # val = hand.get_value()
            # Adjust value label position if cards are spread out more
            # self.dealer_canvas.create_text(10, self.CARD_HEIGHT + 15, text=f"Value: {val}", anchor=tk.W, fill="white", font=("Arial", 10, "bold"))

    def _draw_player_hands(self):
        """Renders the player's hands (supports multiple for splits)."""
        # Clear existing canvases and their parent frames to prevent cumulative packing issues
        for widget in self.player_hands_container.winfo_children():
            widget.destroy()
        self.player_canvases = []

        if not self.game.player.hands[0].cards:
            return

        # Clear existing column configurations to ensure dynamic centering works on updates
        num_cols = self.player_hands_container.grid_size()[0]
        for i in range(num_cols + 2): # Clear all potential columns, including spacers
            self.player_hands_container.grid_columnconfigure(i, weight=0)

        # Add 'spacer' columns on either side to center the player hands group
        self.player_hands_container.grid_columnconfigure(0, weight=1)
        self.player_hands_container.grid_columnconfigure(len(self.game.player.hands) + 1, weight=1)

        card_overlap_x = int(self.CARD_WIDTH * 0.4) # Overlap by 40% for visual appeal, consistent with dealer
        max_cards_per_hand = 8 # Assuming a reasonable maximum to size the canvas
        canvas_width = self.CARD_WIDTH + (max_cards_per_hand - 1) * card_overlap_x

        for i, hand in enumerate(self.game.player.hands):
            # Create a sub-frame for each hand to contain its label and canvas
            hand_frame = tk.Frame(self.player_hands_container, bg="#2e7d32")
            # Place hand frames in the grid, offset by 1 due to the leading spacer column
            hand_frame.grid(row=0, column=i + 1, padx=int(10 * self.CARD_SCALE_FACTOR), pady=int(5 * self.CARD_SCALE_FACTOR))
            
            # Highlight current hand
            bg_color = "#388e3c" if i == self.game.current_hand_index and self.game.state == GameState.PLAYER_TURN else "#2e7d32"
            title = f"Hand {i+1}" if len(self.game.player.hands) > 1 else "Your Hand"
            
            label = tk.Label(hand_frame, text=title, bg=bg_color, fg="white", font=("Arial", int(10 * self.CARD_SCALE_FACTOR), "bold"))
            label.pack(pady=(0, int(5 * self.CARD_SCALE_FACTOR)))
            
            canvas = tk.Canvas(hand_frame, width=canvas_width, height=self.CARD_HEIGHT + int(40 * self.CARD_SCALE_FACTOR), bg=bg_color,
                               highlightthickness=1 if i == self.game.current_hand_index and self.game.state == GameState.PLAYER_TURN else 0,
                               highlightbackground="yellow")
            canvas.pack()
            self.player_canvases.append(canvas)
            
            for j, card in enumerate(hand.cards):
                # Calculate start_x to center cards within this hand's canvas
                total_current_hand_width = self.CARD_WIDTH + (len(hand.cards) - 1) * card_overlap_x
                start_x = (canvas_width / 2) - (total_current_hand_width / 2)
                self._draw_card(canvas, card, start_x + j * card_overlap_x, int(10 * self.CARD_SCALE_FACTOR))
            
            # val = hand.get_value()
            status = ""
            if hand.is_blackjack(): status = " - BLACKJACK!"
            elif hand.is_bust(): status = " - BUST!"
            elif hand.is_stayed: status = " - Stayed"
            
            # canvas.create_text(10, self.CARD_HEIGHT + 25, text=f"Value: {val}{status}", anchor=tk.W, fill="white", font=("Arial", 10, "bold"))

if __name__ == "__main__":
    root = tk.Tk()
    game = BlackjackGame("Player")
    ui = BlackjackUI(root, game)
    root.mainloop()
