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

    def identify(self, value, suit):
        return self.value == value and self.suit == suit

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

    def __getitem__(self, item):
        return self.cards[item]

    def find_card(self, value, suit):
        for c in self:
            if c.identify(value, suit):
                return c
        raise LookupError

    def find_value(self, value):
        for c in self:
            if c.value == value:
                return True
        return False

    def find_suit(self, suit):
        for c in self:
            if c.suit == suit:
                return True
        return False

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
    def __init__(self, name='John', cash=1000):
        self.name = name
        self.hand = Hand()
        self.table = None
        self.cash = cash

    def __len__(self):
        return len(self.hand)

    def __repr__(self):
        return f'{self.name}, {self.cash} {f", {self.hand}" if self.hand else ""}'


class Table:
    def __init__(self):
        self.pile = Hand().deck()
        self.scrap = Hand()
        self.cash = 0
        self.players = []
        self.shuffle_deck()

    def __len__(self):
        return len(self.players)

    def add_player(self, name):
        player = Player(name)
        player.table = self
        self.players.append(player)

    def remove_player(self, name):
        for i, p in enumerate(self.players):
            if p.name == name:
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

    def _find_and_scrap(self, hand, value, suit):
        try:
            i = hand.find_card(value, suit)
            card = hand.pop_card(i)
            self.scrap.add_card(card)
        except LookupError:
            raise LookupError

    def deck_scrap_card(self):
        self._hand_scrap_card(self.pile)

    def player_scrap_card(self, player, card):
        for i, _ in enumerate(player.hand):
            c = player.hand[i]
            if c == card:
                player.hand.pop_card(i)
                self.scrap.add_card(card)
        raise LookupError

    def deal_card_to_player(self, p):
        c = self.pile.pop_card(0)
        p.hand.add_card(c)

    def deal_cards_to_all(self, n):
        for _ in range(n):
            for p in self.players:
                self.deal_card_to_player(p)

    def __repr__(self):
        return f'{len(self)} players. {len(self.pile)} cards in deck, {len(self.scrap)} cards in scrap'


class BlackJack:
    def __init__(self):
        self.table = Table()
        self.table.add_player('dealer')
        self.collect_player_names()
        while True:
            if input('Quit? ') == 'y':
                break
            self.game()

    def collect_player_names(self):
        while True:
            if input('add player? ') != 'y':
                break
            name = input('player name: ')
            self.table.add_player(name)

    def collect_bets(self):
        bets = dict()
        for p in self.table.players:
            if p.name == 'dealer':
                continue
            bet = int(input(f"{p.name}'s bet: "))
            p.cash -= bet
            bets[p] = 2 * bet
        return bets

    def game(self):
        bets = self.collect_bets()
        self.table.deal_cards_to_all(2)
        for p in self.table.players:
            print(f'Current player: {p}')
            self.player_loop(p)
        dealer_sum = 0
        for p in self.table.players:
            if p.name == 'dealer':
                dealer_sum = self.eval_player(p)
                print(f'dealer has {dealer_sum}')
                continue
            player_sum = self.eval_player(p)
            print(f'{p.name} has {player_sum}')
            winner = p if player_sum > dealer_sum else (self.table if player_sum < dealer_sum else None)
            if winner:
                winner.cash += bets[p]
            bets[p] = 0
            for c in p.hand:
                self.table.player_scrap_card(p, c)
        self.table.move_scrap_to_deck()
        self.table.shuffle_deck()

    @staticmethod
    def eval_hand(player):
        h = player.hand
        sum = 0
        for card in h:
            val = card.value
            sum += 10 * (val >= 10) + val * (val < 10)
        return sum

    def eval_player(self, player):
        ev = self.eval_hand(player)
        if ev > 21:
            return False
        if player.hand.find_value(1) and ev <= 11:
            return ev + 10
        return ev

    def player_loop(self, player):
        if player.name == 'dealer':
            return self.dealer_loop(player)
        while True:
            print(player)
            if input('H/S? ') == 'S':
                break
            self.table.deal_card_to_player(player)
            if self.eval_hand(player) > 21:
                break

    def dealer_loop(self, dealer):
        while True:
            if self.eval_player(dealer) < 17:
                self.table.deal_card_to_player(dealer)
                continue
            if self.eval_player(dealer) == 17 and self.eval_hand(dealer) == 7:
                self.table.deal_card_to_player(dealer)
                continue
            break

bj = BlackJack()
