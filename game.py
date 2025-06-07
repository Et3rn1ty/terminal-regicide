from player import Player
from playing_cards import Deck
import terminal_ui
import random

class Game:
    def __init__(self, player1_name):
        self.player1 = Player(player1_name)
        self.player_deck = Deck()
        self.castle_deck = Deck()
        self.discard_pile = []
        self.current_enemy = None
        self.max_hand = 8

    def deal_cards(self):
        # Create an empty deck to store the separated face cards
        self.castle_deck.cards = [] # Clear the initial cards from the new deck

        # Define the ranks of face cards to be removed (excluding Ace)
        face_card_ranks = ["Jack", "Queen", "King"]

        # Initialize a list to hold cards that will remain in the original deck
        cards_to_keep = []

        # Iterate through the cards in the original deck
        for card in self.player_deck.cards:
            if card.rank in face_card_ranks:
                # If it's a face card, add it to the castle_deck
                self.castle_deck.cards.append(card)
            else:
                # Otherwise, keep it in the original deck
                cards_to_keep.append(card)
        
        # Update the original deck's cards to only include those that were kept
        self.player_deck.cards = cards_to_keep
        # Sort the face cards by their rank value (Jack < Queen < King)
        self.castle_deck.cards.sort(key=lambda card: card.rank_value)

        # Group cards by rank to shuffle suits within each rank
        grouped_by_rank = {}
        for card in self.castle_deck.cards:
            if card.rank not in grouped_by_rank:
                grouped_by_rank[card.rank] = []
            grouped_by_rank[card.rank].append(card)
        
        # Shuffle the cards within each rank group
        shuffled_face_cards = []
        for rank in reversed(face_card_ranks): # Ensure consistent order of ranks
            if rank in grouped_by_rank:
                random.shuffle(grouped_by_rank[rank])
                shuffled_face_cards.extend(grouped_by_rank[rank])
        self.castle_deck.cards = shuffled_face_cards

        self.player_deck.shuffle()
        for _ in range(8):
            card = self.player_deck.deal_card()
            self.player1.add_card(card)

        self.current_enemy = self.castle_deck.deal_card()
        self.set_health()

    def set_health(self):
        if self.current_enemy:
            match self.current_enemy.rank_value:
                case 11:
                    health = 10
                case 12:
                    health = 20
                case 13:
                    health = 30
                case _: # The wildcard pattern, similar to 'default'
                    health = 0
            self.current_enemy.health =  health


    def display_enemy(self):
        if self.current_enemy:
            print("Current Enemy:")
            print(self.current_enemy.print_card())
        else:
            print("No current enemy.")

    def play_round(self):
        # Step 1 - Play a card or yield
        action = input("(A)nimal companions can be included (ex. '1, 3' where 3 is an Ace)\n" \
                       "Combos can be played (ex. '1, 3' where 1 and 3 have the same value up to a total of 10)\n" \
                        "Play a card (enter the card number 1-8) or (Y)ield: "
                       "").lower()
        #clear prior shield
        self.shield = 0

        if action in ["yield","y"]:
            # Step 4 - Suffer damage from the enemy
            self.suffer_damage()
        else:
            try:
                stripped = list(map(str.strip, action.split(',')))
                if len(stripped) == 1:
                    card_index = int(action) - 1
                    card = self.player1.hand.pop(card_index)
                    print(f"You played: {card}")
                    # Step 2 - Activate the suit power
                    self.activate_suit_power(card)
                    # Step 3 - Deal damage to the enemy and check
                    self.deal_damage(card)
                    # Step 4 - Suffer damage from the enemy
                    self.suffer_damage()
                else:
                    cards_played = []
                    for c in stripped:
                        cards_played.append(self.player1.hand[int(c)-1])
                    if 1 in set(card.rank_value for card in cards_played):
                        for c in cards_played:
                            self.activate_suit_power(c)
                        for c in cards_played:
                            if c.rank_value==1:
                                self.deal_damage(c,max(card.rank_value for card in cards_played))
                            else:
                                self.deal_damage(c,1)
                            self.player1.hand.remove(c)
                        self.suffer_damage()
                    elif len(set(card.rank_value for card in cards_played)) == 1:
                        if sum(set(card.rank_value for card in cards_played)) > 10:
                            print("Combo value too high, must be less than 10.")
                            self.play_round()
                        else:
                            for c in cards_played:
                                self.activate_suit_power(c)
                            for c in cards_played:
                                self.deal_damage(c)
                                self.player1.hand.remove(c)
                            self.suffer_damage()
                            

            except (ValueError, IndexError) as e:
                print("Invalid input. Please enter a card number or 'yield'.")

    def activate_suit_power(self, card):
        if card.suit == "Hearts":
            print("Hearts power activated!")
            self.heal_from_discard(card.rank_value)
        elif card.suit == "Diamonds":
            print("Diamonds power activated!")
            self.draw_cards(card.rank_value)
        elif card.suit == "Clubs":
            print("Clubs power activated!")
            self.double_damage = True
        elif card.suit == "Spades":
            print("Spades power activated!")
            if not hasattr(self, 'shield'):
                self.shield = 0
            self.shield += card.rank_value

    def draw_cards(self, value):
        print(f"Drawing {value} cards")
        for _ in range(value):
            if len(self.player1.hand) < self.max_hand:
                card = self.player_deck.deal_card()
                if card:
                    self.player1.add_card(card)
                    print(f"Drew {card}")
                else:
                    print("No more cards in the deck to draw.")
                    break
            else:
                print('Reached max hand size.')
                break
        self.display_enemy()
        self.display_hand()

    def heal_from_discard(self, value):
        if not self.discard_pile:
            print("Discard pile is empty.")
            return
        print(f"Healing {value} from discard pile")

        random.shuffle(self.discard_pile)
        heal_cards = self.discard_pile[:value]
        self.discard_pile = self.discard_pile[value:]

        print(f"Adding {len(heal_cards)} cards to the Tavern deck.")
        # Add cards to tavern deck (bottom)
        self.player_deck.cards = heal_cards + self.player_deck.cards

        # Return the discard pile to the table, faceup.
        print("Returning discard pile to the table.")

    def deal_damage(self, card, override=0):
        damage = card.rank_value + override
        if hasattr(self, 'double_damage') and self.double_damage:
            damage *= 2
            del self.double_damage
        print(f"You dealt {damage} damage!")
        if self.current_enemy:
            self.current_enemy.health -= damage
                    
    def suffer_damage(self):
        print("You suffered damage!")
        enemy_attack = self.current_enemy.rank_value
        if hasattr(self, 'shield'):
            enemy_attack -= self.shield
            del self.shield
        print(f"Enemy attacks for {enemy_attack} damage!")
        self.display_hand()
        # Step 4 - Discard cards from hand
        self.discard_cards(enemy_attack)

    def discard_cards(self, damage):
        discarded_value = 0
        hand_value = 0
        discarded_cards = []
        for c in self.player1.hand:
            hand_value += c.rank_value
        if hand_value <= damage:
            print("You cannot discard enough cards to satisfy the damage, you die.")
            exit()

        action = input(f"Discard cards with enough value to cover {damage} damage. (ex. 1, 2, 3)")
        #check if card indexes sent value is greater than damage
        try:
            stripped = list(map(str.strip, action.split(',')))
            print(stripped)
            for c in stripped:
                card = self.player1.hand[int(c)-1]
                discarded_value += card.rank_value
                discarded_cards.append(card)
                print(f"Discarded {card} (total: {discarded_value})")
            if discarded_value < damage:
                print('Not enough value was discarded to cover damage.')
                self.discard_cards(damage)
            else:
                self.player1.hand = [c for c in self.player1.hand if c not in discarded_cards]
                self.discard_pile.extend(discarded_cards)
                self.check_enemy_defeated()
        except (ValueError, IndexError) as e:
            print("Invalid input. Please enter a card numbers to discard.")
            self.discard_cards(damage)


    def check_enemy_defeated(self):
        if self.current_enemy.health < 0:
            print("Enemy defeated!")
            self.discard_pile.append(self.current_enemy)
            self.current_enemy = self.castle_deck.deal_card()
            self.set_health()
        if self.current_enemy == 0:
            print("Perfect defeat, adding enemy to tavern.")
            self.player_deck = [self.current_enemy] + self.player_deck
            self.current_enemy = self.castle_deck.deal_card()
            self.set_health()

    def display_hand(self):
        print("Your hand:")
        cards = []
        if self.player1.hand:
            for card in self.player1.hand:
                cards.append(card.print_card())

            # Split each card string into individual lines
            cards_as_lines = [card.splitlines() for card in cards]

            # Assuming all cards have the same number of lines
            num_lines_per_card = len(cards_as_lines[0])

            # Iterate through each line of the cards
            for i in range(num_lines_per_card):
                # Print the i-th line from each card, joined by a space
                print(" ".join(card_lines[i] for card_lines in cards_as_lines))
        else:
            print("You're out of cards, you die.")
            exit()

            

    def play_game(self):
        self.deal_cards()
        try:
            while self.current_enemy:
                self.display_enemy()
                self.display_hand()
                self.play_round()
        except KeyboardInterrupt:
            print("\nExiting Game.")
            exit()

if __name__ == "__main__":
    player1_name = terminal_ui.run_game()
    if player1_name:
        game = Game(player1_name)
        game.play_game()
