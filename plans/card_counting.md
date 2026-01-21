# Plan: Card Counting Feature (Hi-Lo System)

This document outlines the implementation of a card counting feature for the Blackjack Trainer.

## 1. Core Logic (src/blackjack/game.py & src/blackjack/models.py)

### 1.1. Hi-Lo Counting
- Define a mapping for card ranks to their Hi-Lo values:
    - 2, 3, 4, 5, 6: +1
    - 7, 8, 9: 0
    - 10, J, Q, K, A: -1
- Add a `running_count` attribute to the `BlackjackGame` class, initialized to 0.

### 1.2. Tracking Dealt Cards
- Update `BlackjackGame.start_round` and other methods that deal cards to update the `running_count`.
- **Crucial**: Modify `BlackjackGame` to stop reshuffling the deck every round. Implement a penetration limit (e.g., 75% of the deck) before automatic reshuffling occurs. Reset `running_count` only when the deck is reshuffled.

### 1.3. Count Query Logic
- Add `hands_until_next_query` to `BlackjackGame`.
- After each round, decrement this counter.
- When it reaches 0, trigger a flag `needs_count_verification`.
- Randomize the next query interval (1-3 hands) after each query.

## 2. User Interface (src/gui_main.py)

### 2.1. Incremental Dealer Play
- Modify how the dealer plays to allow for a visual delay.
- Use `root.after(750, ...)` in `BlackjackUI` to add cards one by one until the dealer's hand reaches 17 or busts.
- This ensures the user has time (~0.75s per card) to update their mental count.

### 2.2. Count Verification Dialog
- When `needs_count_verification` is True at the end of a round:
    - Use `tkinter.simpledialog.askinteger` to prompt the user for the current running count.
    - Provide feedback:
        - If correct: "Correct! The count is [X]."
        - If incorrect: "Incorrect. The correct count was [X]."
    - Reset the `hands_until_next_query` and `needs_count_verification` flag.

### 2.3. Constraints
- Ensure the `running_count` is **never** displayed in the UI during normal play.

## 3. Implementation Steps

1.  **Refactor Deck Persistence**: Modify `BlackjackGame` to keep the same deck between rounds until a certain depth is reached.
2.  **Implement Running Count**: Add logic to track the Hi-Lo count as cards are dealt.
3.  **Implement Incremental Dealer Play**: Update the GUI to animate dealer hits with a 0.75s delay.
4.  **Add Query Logic**: Implement the random hand interval tracking and the verification dialog.
5.  **Testing**: Verify count accuracy and query frequency.
