class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []

    def add_card(self, card):
        self.hand.append(card)

    def play_card(self):
        if self.hand:
            return self.hand.pop(0)
        else:
            return None

    def has_cards(self):
        return len(self.hand) > 0
