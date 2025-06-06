class Card:
    """Represents a standard playing card."""

    def __init__(self, suit, rank):
        """
        Initializes a card.
        """
        rank_values = {
            "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
            "Jack": 11, "Queen": 12, "King": 13, "Ace": 1
        }
        self.suit = suit
        self.rank = rank
        self.rank_value = rank_values[rank]

    def __str__(self):
        """Returns a string representation of the card."""
        return f"{self.rank} of {self.suit}"

    def __repr__(self):
        """Returns a string representation of the card for debugging."""
        return f"Card(suit='{self.suit}', rank='{self.rank}')"

    def __gt__(self, other):
        """Compares two cards based on their rank value."""
        return self.rank_value > other.rank_value
    
    def print_card(self):
        """Prints an ASCII representation of a single playing card. ('♠', '♥', '♦', '♣')"""
        rank = self.rank
        match self.suit:
            case "Hearts":
                suit = '♥'
            case "Spades":
                suit = '♠'
            case "Clubs":
                suit = '♣'
            case "Diamonds":
                suit = '♦'
        top = "┌─────────┐"
        bottom = "└─────────┘"
        side = "│         │"

        if rank == "10":  # Ten is the only rank with two digits
            rank_right = rank
            rank_left = rank
        else:
            rank_right = rank[0] + " "
            rank_left = " " + rank[0]

        suit_line = f"│    {suit}    │"
        rank_line_left = f"│{rank_left}       │"
        rank_line_right = f"│       {rank_right}│"

        card = top +'\n'+ rank_line_left+'\n'+ side+'\n'+ suit_line+'\n'+ side+'\n'+ rank_line_right+'\n'+ bottom+'\n'
        return card

class Deck:
    """Represents a deck of playing cards."""

    def __init__(self):
        """Initializes a deck of cards with standard 52 cards."""
        self.suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
        self.ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace"]
        self.cards = self._create_deck()

    def _create_deck(self):
        """Creates a standard 52-card deck."""
        return [Card(suit, rank) for suit in self.suits for rank in self.ranks]

    def shuffle(self):
        """Shuffles the deck of cards."""
        import random
        random.shuffle(self.cards)

    def deal_card(self):
        """Deals a single card from the deck."""
        if self.cards:
            return self.cards.pop()
        else:
            return None

    def has_cards(self):
        """Returns True if the deck has cards, False otherwise."""
        return bool(self.cards)

    def __str__(self):
        """Returns a string representation of the deck."""
        return f"Deck with {len(self.cards)} cards"

    def __repr__(self):
        """Returns a string representation of the deck for debugging."""
        return f"Deck(cards={self.cards})"
