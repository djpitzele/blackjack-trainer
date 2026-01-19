import random
from typing import List, Optional

class Card:
    """Represents a single playing card."""
    def __init__(self, rank: str, suit: str):
        self.rank = rank
        self.suit = suit

    @property
    def value(self) -> int:
        """Returns the numeric value of the card in Blackjack."""
        if self.rank in ['J', 'Q', 'K']:
            return 10
        if self.rank == 'A':
            return 11  # Aces are handled dynamically in Hand.get_value()
        return int(self.rank)

    def __repr__(self):
        return f"{self.rank}{self.suit}"

class Deck:
    """Represents a deck of 52 cards."""
    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    SUITS = ['♠', '♥', '♦', '♣']

    def __init__(self, num_decks: int = 1):
        self.cards: List[Card] = []
        for _ in range(num_decks):
            for suit in self.SUITS:
                for rank in self.RANKS:
                    self.cards.append(Card(rank, suit))
        self.shuffle()

    def shuffle(self):
        """Shuffles the deck."""
        random.shuffle(self.cards)

    def deal(self) -> Card:
        """Deals a single card from the deck."""
        if not self.cards:
            raise ValueError("No cards left in the deck.")
        return self.cards.pop()

class Hand:
    """Represents a hand of cards for a player or dealer."""
    def __init__(self, is_from_split: bool = False):
        self.cards: List[Card] = []
        self.is_stayed = False
        self.is_from_split = is_from_split

    def add_card(self, card: Card):
        """Adds a card to the hand."""
        self.cards.append(card)

    def get_value(self) -> int:
        """Calculates the best possible value of the hand."""
        value = sum(card.value for card in self.cards)
        aces = sum(1 for card in self.cards if card.rank == 'A')

        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
        return value

    def is_bust(self) -> bool:
        """Returns True if the hand value exceeds 21."""
        return self.get_value() > 21

    def is_blackjack(self) -> bool:
        """Returns True if the hand is a natural blackjack (21 with 2 cards)."""
        if self.is_from_split:
            return False
        return len(self.cards) == 2 and self.get_value() == 21

    def can_split(self) -> bool:
        """Checks if the hand can be split (two cards of the same rank)."""
        return len(self.cards) == 2 and self.cards[0].rank == self.cards[1].rank

    def can_double_down(self) -> bool:
        """Checks if the hand can be doubled down (typically allowed on first two cards)."""
        return len(self.cards) == 2

    def __repr__(self):
        return f"{self.cards} (Value: {self.get_value()})"

class Participant:
    """Base class for a game participant (Player or Dealer)."""
    def __init__(self, name: str):
        self.name = name
        self.hands: List[Hand] = [Hand()]

    def reset(self):
        """Resets the participant for a new round."""
        self.hands = [Hand()]

class Player(Participant):
    """Represents a human player."""
    def __init__(self, name: str):
        super().__init__(name)

class Dealer(Participant):
    """Represents the dealer."""
    def __init__(self):
        super().__init__("Dealer")

    def should_hit(self) -> bool:
        """Dealer hits on anything less than 17 (standard rule)."""
        # Standard rule: Stand on all 17s. 
        # Some variants hit on soft 17, but we'll stick to stand on 17.
        return self.hands[0].get_value() < 17
