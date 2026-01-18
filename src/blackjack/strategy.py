from typing import List
from .models import Card, Hand

# Dealer Upcard Columns: 2, 3, 4, 5, 6, 7, 8, 9, 10, A
DEALER_UPCARDS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'A']

# Strategy tables based on the provided image
PERFECT_PLAY_TABLES = {
    "hard_totals": {
        5:    ['H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H'],
        6:    ['H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H'],
        7:    ['H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H'],
        8:    ['H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H'],
        9:    ['H', 'D', 'D', 'D', 'D', 'H', 'H', 'H', 'H', 'H'],
        10:   ['D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'H', 'H'],
        11:   ['D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'H'],
        12:   ['H', 'H', 'S', 'S', 'S', 'H', 'H', 'H', 'H', 'H'],
        13:   ['S', 'S', 'S', 'S', 'S', 'H', 'H', 'H', 'H', 'H'],
        14:   ['S', 'S', 'S', 'S', 'S', 'H', 'H', 'H', 'H', 'H'],
        15:   ['S', 'S', 'S', 'S', 'S', 'H', 'H', 'H', 'H', 'H'],
        16:   ['S', 'S', 'S', 'S', 'S', 'H', 'H', 'H', 'H', 'H'],
        17:   ['S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'], # 17+
    },
    "soft_totals": {
        13:   ['H', 'H', 'H', 'D', 'D', 'H', 'H', 'H', 'H', 'H'], # A,2
        14:   ['H', 'H', 'H', 'D', 'D', 'H', 'H', 'H', 'H', 'H'], # A,3
        15:   ['H', 'H', 'D', 'D', 'D', 'H', 'H', 'H', 'H', 'H'], # A,4
        16:   ['H', 'H', 'D', 'D', 'D', 'H', 'H', 'H', 'H', 'H'], # A,5
        17:   ['H', 'D', 'D', 'D', 'D', 'H', 'H', 'H', 'H', 'H'], # A,6
        18:   ['S', 'D', 'D', 'D', 'D', 'S', 'S', 'H', 'H', 'H'], # A,7 (DS treated as D)
        19:   ['S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'], # A,8
        20:   ['S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'], # A,9
    },
    "pairs": {
        '2':  ['P', 'P', 'P', 'P', 'P', 'P', 'H', 'H', 'H', 'H'],
        '3':  ['P', 'P', 'P', 'P', 'P', 'P', 'H', 'H', 'H', 'H'],
        '4':  ['H', 'H', 'H', 'P', 'P', 'H', 'H', 'H', 'H', 'H'],
        '5':  ['D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'H', 'H'],
        '6':  ['P', 'P', 'P', 'P', 'P', 'H', 'H', 'H', 'H', 'H'],
        '7':  ['P', 'P', 'P', 'P', 'P', 'P', 'H', 'H', 'H', 'H'],
        '8':  ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
        '9':  ['P', 'P', 'P', 'P', 'P', 'S', 'P', 'P', 'S', 'S'],
        'T':  ['S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'], # 10s, Jacks, Queens, Kings
        'A':  ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
    }
}

def get_recommended_move(player_hand: Hand, dealer_upcard: Card) -> str:
    """Returns the recommended move based on Basic Strategy.

    Args:
        player_hand: The player's current hand.
        dealer_upcard: The dealer's visible upcard.

    Returns:
        The recommended move ('H', 'S', 'P', or 'D').
    """
    dealer_rank = dealer_upcard.rank
    if dealer_rank in ['J', 'Q', 'K']:
        dealer_rank = '10'
    upcard_index = DEALER_UPCARDS.index(dealer_rank)

    # 1. Check for Pairs
    if player_hand.can_split() and len(player_hand.cards) == 2:
        pair_rank = player_hand.cards[0].rank
        if pair_rank in ['J', 'Q', 'K']:
            pair_rank = 'T' # Represent 10-value cards as 'T' for table lookup
        elif pair_rank == 'A':
            pair_rank = 'A'
        elif pair_rank == '10':
             pair_rank = 'T'
        
        if pair_rank in PERFECT_PLAY_TABLES["pairs"]:
            return PERFECT_PLAY_TABLES["pairs"][pair_rank][upcard_index]

    # 2. Check for Soft Totals (has an Ace counting as 11)
    # A hand is considered "soft" if it contains an Ace that can be counted as 11
    # without busting, and if changing it to 1 wouldn't change the value below 21 unless it's an Ace-only scenario
    if any(card.rank == 'A' for card in player_hand.cards) and player_hand.get_value() <= 21:
        # Check if it's truly a soft hand by trying to make the Ace a 1
        temp_value_if_ace_is_1 = 0
        num_aces = 0
        for card in player_hand.cards:
            if card.rank == 'A':
                num_aces += 1
                temp_value_if_ace_is_1 += 1 # Count Ace as 1 initially
            else:
                temp_value_if_ace_is_1 += card.value
        
        # If there's an Ace and counting it as 11 makes it a soft total (not hard or busted)
        # and if the total with all Aces as 1 is different from the get_value, it's soft
        # This handles cases like A,A,A where only one A is 11
        if num_aces > 0 and player_hand.get_value() != temp_value_if_ace_is_1:
             # Special handling for A,A = 12 (soft 12), not A,A,2=14
            if len(player_hand.cards) == 2 and player_hand.cards[0].rank == 'A' and player_hand.cards[1].rank == 'A':
                # This case is handled by pairs. If we didn't split, it effectively becomes a hard 12 for strategy purposes IF we didn't split
                pass # Let it fall through to hard totals if not split
            else:
                soft_total = player_hand.get_value()
                # The soft total keys in the table are the actual hand values
                if soft_total >= 13 and soft_total <= 20:
                    return PERFECT_PLAY_TABLES["soft_totals"][soft_total][upcard_index]

    # 3. Hard Totals
    hard_total = player_hand.get_value()
    if hard_total < 5:
        return 'H' # Always hit on less than 5
    elif hard_total >= 17:
        return 'S' # Always stand on 17+
    else:
        return PERFECT_PLAY_TABLES["hard_totals"][hard_total][upcard_index]
