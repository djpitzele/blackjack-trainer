from .models import Deck, Player, Dealer, Hand, Card
from .strategy import get_recommended_move
from enum import Enum, auto
import random
from typing import Optional

DECK_PEN = 0.75

class GameState(Enum):
    PLAYER_TURN = auto()
    DEALER_TURN = auto()
    ROUND_OVER = auto()

class BlackjackGame:
    """Manages the flow and logic of a Blackjack game."""
    def __init__(self, player_name: str, num_decks: int = 6):
        self.num_decks = num_decks
        self.deck = Deck(num_decks=num_decks)
        self.player = Player(player_name)
        self.dealer = Dealer()
        self.state = GameState.ROUND_OVER
        self.current_hand_index = 0
        self.last_move_feedback: Optional[dict] = None
        self.running_count = 0
        self.hands_until_next_query = random.randint(1, 3)
        self.needs_count_verification = False

    def _deal_card(self) -> Card:
        """Deals a card and updates the running count."""
        card = self.deck.deal()
        self.running_count += card.get_hi_lo_value()
        return card

    def start_round(self):
        """Initializes a new round."""
        if self.state != GameState.ROUND_OVER:
            raise RuntimeError("Cannot start round in current state.")

        self.player.reset()
        self.dealer.reset()
        
        # Check for reshuffle (75% penetration)
        penetration = (self.deck.total_cards - self.deck.remaining_cards) / self.deck.total_cards
        if penetration > DECK_PEN:
            self.deck = Deck(num_decks=self.num_decks)
            self.running_count = 0

        # Initial deal
        self.player.hands[0].add_card(self._deal_card())
        self.dealer.hands[0].add_card(self._deal_card())
        self.player.hands[0].add_card(self._deal_card())
        self.dealer.hands[0].add_card(self._deal_card())

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
        hand.add_card(self._deal_card())

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
        """Take one card and stand."""
        if self.state != GameState.PLAYER_TURN:
            raise RuntimeError("Not player's turn.")
        
        hand = self.player.hands[self.current_hand_index]
        if not hand.can_double_down():
            raise RuntimeError("Cannot double down on this hand.")
        
        self._record_move_feedback("D", self.current_hand_index)

        hand.add_card(self._deal_card())
        hand.is_stayed = True
        self._advance_hand()

    def split(self):
        """Split the current hand into two."""
        if self.state != GameState.PLAYER_TURN:
            raise RuntimeError("Not player's turn.")
        
        hand = self.player.hands[self.current_hand_index]
        if not hand.can_split():
            raise RuntimeError("Cannot split this hand.")
        
        self._record_move_feedback("P", self.current_hand_index)

        # Create new hand
        new_hand = Hand(is_from_split=True)
        hand.is_from_split = True
        
        # Move one card to the new hand
        card_to_move = hand.cards.pop()
        new_hand.add_card(card_to_move)
        
        # Deal new cards to both hands
        hand.add_card(self._deal_card())
        new_hand.add_card(self._deal_card())
        
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
            # We don't call dealer_play() here anymore to allow the UI to handle timing.

    def dealer_play(self):
        """Dealer hits until 17 or bust. Note: This happens instantly."""
        if self.state != GameState.DEALER_TURN:
            return

        all_busted = all(hand.is_bust() for hand in self.player.hands)
        if not all_busted:
            while self.dealer_hit_if_needed():
                pass
        
        self.resolve_round()

    def dealer_hit_if_needed(self) -> bool:
        """
        Executes a single dealer hit if appropriate.
        Returns True if a card was dealt, False if the dealer is finished.
        """
        if self.state != GameState.DEALER_TURN:
            return False

        all_busted = all(hand.is_bust() for hand in self.player.hands)
        if not all_busted and self.dealer.should_hit():
            self.dealer.hands[0].add_card(self._deal_card())
            return True
        
        return False

    def resolve_round(self):
        """Determines hand outcomes and manages count queries."""
        self.state = GameState.ROUND_OVER
        self.hands_until_next_query -= 1
        if self.hands_until_next_query <= 0:
            self.needs_count_verification = True

    def get_game_status(self):
        """Returns a summary of the current game state."""
        return {
            "state": self.state.name,
            "player_hands": [str(h) for h in self.player.hands],
            "dealer_hand": str(self.dealer.hands[0]) if self.state == GameState.ROUND_OVER else f"[{self.dealer.hands[0].cards[0]}, ??]"
        }
