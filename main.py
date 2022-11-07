import random as rand


class Card:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit
        self.index = 10 * value + suit

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
        return None

    def find_value(self, value):
        for c in self:
            if c.value == value:
                return c
        return None

    def find_suit(self, suit):
        for c in self:
            if c.suit == suit:
                return c
        return None

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

    def move_hand_to_scrap(self, player):
        hand = player.hand
        for _ in range(len(hand)):
            card = hand.pop_card(0)
            self.scrap.add_card(card)

    def move_scrap_to_deck(self):
        for _ in range(len(self.scrap)):
            card = self.scrap.pop_card(0)
            self.pile.add_card(card)

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
    def __init__(self, run=True):
        self.table = Table()
        self.dealer = Player('dealer')
        if run:
            self.main()

    def main(self):
        self.collect_player_names()
        while True:
            self.game()
            if input('Quit? ') == 'y':
                break

    def collect_player_names(self):
        while True:
            if input('add player? ') != 'y':
                break
            name = input('player name: ')
            self.table.add_player(name)
            print(f'{name} has successfully entered the game')

    def collect_bets(self):
        bets = dict()
        for p in self.table.players:
            bet = int(input(f"{p.name}'s turn.\nBalance: {p.cash}\n Bet: "))
            p.cash -= bet
            print(f'{p.name} now has ${p.cash}')
            bets[p] = 2 * bet
        return bets

    def game(self):
        print('Collecting bets...')
        bets = self.collect_bets()
        print('Dealing cards to all players...')
        self.table.deal_cards_to_all(2)
        for _ in range(2):
            self.table.deal_card_to_player(self.dealer)
        print('Now playing.')
        print(f'dealer showing {self.dealer.hand[0]}')
        for p in self.table.players:
            print(f'Current player: {p}')
            self.player_loop(p)
        self.dealer_loop()
        dealer_sum = self.eval_player(self.dealer)
        print(f'dealer has {dealer_sum}.')
        for p in self.table.players:
            player_sum = self.eval_player(p)
            print(f'{p.name} has {player_sum}')
            winner = p if player_sum > dealer_sum else (self.table if player_sum < dealer_sum else None)
            if not winner:
                print('push')
            else:
                winner.cash += bets[p]
                if winner == p:
                    print(f'{p.name} wins!')
                else:
                    print('dealer wins')
            bets[p] = 0
            print(f'now {p.name} has ${p.cash}.')
        for p in self.table.players:
            print(f"now moving {p.name}'s cards to scrap")
            self.table.move_hand_to_scrap(p)
            print(f'now scrap has {len(self.table.scrap)} cards.')
        print('now moving dealer cards to scrap')
        self.table.move_hand_to_scrap(self.dealer)
        print(f'now scrap has {len(self.table.scrap)} cards.')
        print(f'deck has {len(self.table.pile)}. now moving scrap to deck')
        self.table.move_scrap_to_deck()
        print(f'now deck has {len(self.table.pile)} cards and scrap has {len(self.table.scrap)} cards')
        print('shuffling...')
        self.table.shuffle_deck()
        print('done with current round!')

    @staticmethod
    def eval_hand(player):
        h = player.hand
        res = 0
        for card in h:
            val = card.value
            res += 10 * (val >= 10) + val * (val < 10)
        return res

    @staticmethod
    def eval_player(player):
        ev = BlackJack.eval_hand(player)
        if ev > 21:
            return False
        if player.hand.find_value(1) and ev <= 11:
            return ev + 10
        if ev == 21 and len(player.hand) == 2:
            ev += 1
        return ev

    def player_loop(self, player):
        while True:
            hard_ev = self.eval_player(player)
            soft_ev = self.eval_hand(player)
            print(f'{player.hand} {hard_ev}{f"/{soft_ev}" if hard_ev - soft_ev else ""}')
            if input('H/S? ') == 'S':
                break
            self.table.deal_card_to_player(player)
            if self.eval_hand(player) > 21:
                break

    def dealer_loop(self):
        dealer = self.dealer
        while True:
            ev = self.eval_player(dealer)
            soft = self.eval_hand(dealer)
            print(f'dealer hand: {dealer.hand} {ev}{f"/{soft}" if ev - soft else ""}')
            if not ev:
                print('dealer bust')
                break
            if ev < 17:
                print('dealer hits')
                self.table.deal_card_to_player(dealer)
                continue
            if ev == 17 and soft == 7:
                print('dealer hits on soft 17')
                self.table.deal_card_to_player(dealer)
                continue
            print('dealer stays')
            break
