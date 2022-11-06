import random as rand


class Card:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit
        self.index = 10*value + suit

    def __eq__(self, other):
        return self.index == other.index

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        return self.value > other.value

    def __ge__(self, other):
        if self > other:
            return True
        elif self < other:
            return False
        return self.index >= other.index

    def __lt__(self, other):
        return self.value < other.value

    def __le__(self, other):
        if self < other:
            return True
        elif self > other:
            return False
        return self.index <= other.index

    def color(self):
        return self.suit % 2 == 0

    def __repr__(self):
        d1 = {10: 'T', 11: 'J', 12: 'Q', 13: 'K', 1: 'A'}
        d2 = {1: 'C', 2: 'D', 3: 'H', 4: 'S'}
        return f' {d1[self.value] if self.value in d1 else self.value}{d2[self.suit]} '


class Hand:
    @classmethod
    def deck(cls):
        obj = cls()
        for i in range(1, 14):
            for j in range(1, 5):
                obj.add_card(Card(i, j))
        return obj

    def __init__(self):
        self.cards = []

    def __len__(self):
        return len(self.cards)

    def __iter__(self):
        return self.cards.__iter__()

    def __repr__(self):
        return self.cards.__repr__()

    def get_card(self, i):
        return self.cards[i]

    def add_card(self, card):
        self.cards.append(card)

    def pop_card(self, i):
        return self.cards.pop(i)

    def draw_card(self):
        return self.pop_card(0)

    def shuffle(self):
        rand.shuffle(self.cards)


class Player:
    def __init__(self, name='John'):
        self.name = name
        self.hand = Hand()
        self.table = None

    def __len__(self):
        return len(self.hand)


class Table:
    def __init__(self):
        self.pile = Hand().deck()
        self.scrap = Hand()
        self.players = []
        self.shuffle_deck()

    def add_player(self, player):
        self.players.append(player)
        player.table = self

    def remove_player(self, player):
        for i, p in enumerate(self.players):
            if p == player:
                self.players.pop(i)
                p.table = None
                return
        raise LookupError

    def shuffle_deck(self):
        self.pile.shuffle()

    def move_scrap_to_deck(self):
        for i in range(len(self.scrap)):
            c = self.scrap.pop_card(i)
            self.pile.add_card(c)

    def draw_card(self, player):
        c = self.pile.pop_card(0)
        player.hand.add_card(c)

    def _hand_scrap_card(self, hand, card=None):
        if card:
            for i, c in enumerate(hand):
                if c == card:
                    card = hand.pop_card(i)
                    break
        #    raise LookupError
        else:
            card = hand.pop_card(0)
        self.scrap.add_card(card)

    def deck_scrap_card(self):
        self._hand_scrap_card(self.pile)

    def player_scrap_card(self, player, card):
        for i in range(player.hand):
            c = player.hand[i]
            if c == card:
                player.hand.pop_card(i)
                self.scrap.add_card(card)
        raise LookupError

    def deal_card_to_player(self, p):
        c = self.pile.pop_card(0)
        p.hand.add_card(c)

    def deal_cards_to_all(self, n):
        for _ in n:
            for p in self.players:
                self.deal_card_to_player(p)
