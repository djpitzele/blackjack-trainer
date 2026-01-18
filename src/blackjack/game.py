from .models import Deck, Player, Dealer, Hand, Card
from .strategy import get_recommended_move
from enum import Enum, auto

class GameState(Enum):
    BETTING = auto()
    PLAYER_TURN = auto()
    DEALER_TURN = auto()
    ROUND_OVER = auto()

class BlackjackGame:
    """Manages the flow and logic of a Blackjack game."""
    def __init__(self, player_name: str, bankroll: int = 1000, num_decks: int = 6):
        self.deck = Deck(num_decks=num_decks)
        self.player = Player(player_name, bankroll)
        self.dealer = Dealer()
        self.state = GameState.BETTING
        self.current_hand_index = 0
        self.last_move_feedback: Optional[dict] = None

    def start_round(self, bet_amount: int):
        """Initializes a new round with a bet."""
        if self.state != GameState.BETTING and self.state != GameState.ROUND_OVER:
            raise RuntimeError("Cannot start round in current state.")
        
        if bet_amount > self.player.bankroll:
            raise ValueError("Insufficient bankroll.")

        self.player.reset()
        self.dealer.reset()
        self.deck = Deck(num_decks=6) # Reshuffle every round for simplicity or track penetration
        
        self.player.place_bet(bet_amount)
        
        # Initial deal
        self.player.hands[0].add_card(self.deck.deal())
        self.dealer.hands[0].add_card(self.deck.deal())
        self.player.hands[0].add_card(self.deck.deal())
        self.dealer.hands[0].add_card(self.deck.deal())

        self.state = GameState.PLAYER_TURN
        self.current_hand_index = 0
        self.last_move_feedback = None

        # Check for immediate Blackjack
        if self.player.hands[0].is_blackjack() or self.dealer.hands[0].is_blackjack():
            self.state = GameState.DEALER_TURN # Move to resolution
            self.resolve_round()

    def _record_move_feedback(self, player_move: str, hand_index: int):
        player_hand = self.player.hands[hand_index]
        dealer_upcard = self.dealer.hands[0].cards[0] # Dealer's visible card
        recommended_move = get_recommended_move(player_hand, dealer_upcard)

        is_correct = (player_move == recommended_move)
        self.last_move_feedback = {
            "player_move": player_move,
            "recommended_move": recommended_move,
            "is_correct": is_correct,
            "hand_index": hand_index
        }

    def get_perfect_play_advice(self, hand_index: int) -> str:
        """Returns the recommended move for a given hand index without executing it."""
        player_hand = self.player.hands[hand_index]
        dealer_upcard = self.dealer.hands[0].cards[0]
        return get_recommended_move(player_hand, dealer_upcard)

    def hit(self):
        """Current hand takes a card."""
        if self.state != GameState.PLAYER_TURN:
            raise RuntimeError("Not player's turn.")
        
        self._record_move_feedback("H", self.current_hand_index)
        
        hand = self.player.hands[self.current_hand_index]
        hand.add_card(self.deck.deal())

        if hand.is_bust():
            self._advance_hand()

    def stand(self):
        """Current hand stands."""
        if self.state != GameState.PLAYER_TURN:
            raise RuntimeError("Not player's turn.")
        
        self._record_move_feedback("S", self.current_hand_index)

        self.player.hands[self.current_hand_index].is_stayed = True
        self._advance_hand()

    def double_down(self):
        """Double the bet, take one card, and stand."""
        if self.state != GameState.PLAYER_TURN:
            raise RuntimeError("Not player's turn.")
        
        hand = self.player.hands[self.current_hand_index]
        if not hand.can_double_down():
            raise RuntimeError("Cannot double down on this hand.")
        
        if self.player.bankroll < hand.bet:
            raise ValueError("Insufficient bankroll to double down.")
        
        self._record_move_feedback("D", self.current_hand_index)

        self.player.bankroll -= hand.bet
        hand.bet *= 2
        hand.add_card(self.deck.deal())
        hand.is_stayed = True
        self._advance_hand()

    def split(self):
        """Split the current hand into two."""
        if self.state != GameState.PLAYER_TURN:
            raise RuntimeError("Not player's turn.")
        
        hand = self.player.hands[self.current_hand_index]
        if not hand.can_split():
            raise RuntimeError("Cannot split this hand.")
        
        if self.player.bankroll < hand.bet:
            raise ValueError("Insufficient bankroll to split.")
        
        self._record_move_feedback("P", self.current_hand_index)

        # Create new hand
        new_hand = Hand(bet=hand.bet, is_from_split=True)
        hand.is_from_split = True
        self.player.bankroll -= hand.bet
        
        # Move one card to the new hand
        card_to_move = hand.cards.pop()
        new_hand.add_card(card_to_move)
        
        # Deal new cards to both hands
        hand.add_card(self.deck.deal())
        new_hand.add_card(self.deck.deal())
        
        # Add the new hand to the player's list of hands
        # Insert it after the current hand to play it next
        self.player.hands.insert(self.current_hand_index + 1, new_hand)

        # Special rule: Split Aces only get one card
        if hand.cards[0].rank == 'A':
            hand.is_stayed = True
            new_hand.is_stayed = True
            self._advance_hand() # Move past the first Ace hand
            # Note: _advance_hand will call itself recursively via _advance_hand
            # if we are at the end, but here we just moved one.

    def _advance_hand(self):
        """Moves to the next hand or to the dealer's turn."""
        self.current_hand_index += 1
        
        # If we have more hands, check if the next one is already stayed (e.g. from split aces)
        if self.current_hand_index < len(self.player.hands):
            if self.player.hands[self.current_hand_index].is_stayed:
                self._advance_hand()
                return

        if self.current_hand_index >= len(self.player.hands):
            self.state = GameState.DEALER_TURN
            self.dealer_play()

    def dealer_play(self):
        """Dealer hits until 17 or bust."""
        if self.state != GameState.DEALER_TURN:
            return

        # Dealer only plays if player hasn't busted all hands or has a blackjack
        # Actually, standard rules: Dealer plays unless all player hands busted.
        all_busted = all(hand.is_bust() for hand in self.player.hands)
        
        if not all_busted:
            while self.dealer.should_hit():
                self.dealer.hands[0].add_card(self.deck.deal())
        
        self.resolve_round()

    def resolve_round(self):
        """Determines winners and payouts."""
        self.state = GameState.ROUND_OVER
        dealer_hand = self.dealer.hands[0]
        dealer_value = dealer_hand.get_value()
        dealer_bust = dealer_hand.is_bust()
        dealer_bj = dealer_hand.is_blackjack()

        for hand in self.player.hands:
            player_value = hand.get_value()
            player_bust = hand.is_bust()
            player_bj = hand.is_blackjack()

            if player_bust:
                # Loss - bet already deducted
                pass
            elif dealer_bj:
                if player_bj:
                    # Push
                    self.player.add_winnings(hand.bet)
                else:
                    # Loss
                    pass
            elif player_bj:
                # Blackjack pays 3:2
                self.player.add_winnings(int(hand.bet * 2.5))
            elif dealer_bust:
                # Win
                self.player.add_winnings(hand.bet * 2)
            elif player_value > dealer_value:
                # Win
                self.player.add_winnings(hand.bet * 2)
            elif player_value == dealer_value:
                # Push
                self.player.add_winnings(hand.bet)
            else:
                # Loss
                pass

    def get_game_status(self):
        """Returns a summary of the current game state."""
        return {
            "state": self.state.name,
            "player_hands": [str(h) for h in self.player.hands],
            "dealer_hand": str(self.dealer.hands[0]) if self.state == GameState.ROUND_OVER else f"[{self.dealer.hands[0].cards[0]}, ??]",
            "bankroll": self.player.bankroll
        }
