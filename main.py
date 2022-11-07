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
    def deck(cls, n=1):
        obj = cls()
        for _ in range(n):
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
    def __init__(self, num_of_decks=1):
        self.pile = Hand().deck(num_of_decks)
        self.scrap = Hand()
        self.cash = 0
        self.players = []
        self.bets = dict()
        self.shuffle_deck()

    def __len__(self):
        return len(self.players)

    def add_player(self, name, cash=1000):
        player = Player(name, cash)
        player.table = self
        self.players.append(player)
        self.bets[player] = 0
        return player

    def find_player(self, name):
        for p in self.players:
            if p.name == name:
                return p
        raise LookupError

    def remove_player(self, name):
        for i, p in enumerate(self.players):
            if p.name == name:
                self.players.pop(i)
                self.bets.pop(p)
                p.table = None
                return p
        raise LookupError

    def shuffle_deck(self):
        self.pile.shuffle()

    @staticmethod
    def move_card(source, i, target):
        target.add_card(source.pop_card(i))

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
    NUM_OF_DECKS = 6
    SCRAP_LIMIT = 52

    def __init__(self, run=True):
        self.table = Table(self.NUM_OF_DECKS)
        self.dealer = Player('dealer')
        self.ghost_players = []
        if run:
            self.main()

    def main(self):
        self.collect_player_names()
        while True:
            self.game()
            action = input('Quit? ')
            if action == 'y':
                break

    def collect_player_names(self):
        self.table.players.append(self.dealer)
        while True:
            if input('add player? ') != 'y':
                break
            name = input('player name: ')
            self.table.add_player(name)
            print(f'{name} has successfully entered the game')

    def collect_bet(self, player, bet, paying_player=None):
        payer = paying_player if paying_player else player
        payer.cash -= bet
        self.dealer.cash -= bet
        self.table.bets[player] += 2 * bet

    def ask_for_bet(self, player):
        bet = int(input('place bet: '))
        self.collect_bet(player, bet)

    def collect_bets(self):
        collect = False
        for p in self.table.players:
            if not collect:
                collect = True
                continue
            print(f"{p.name}'s turn.\nBalance: {p.cash}")
            self.ask_for_bet(p)

    def loop_all_players(self):
        for p in self.table.players:
            if p == self.dealer:
                continue
            self.player_loop(p)
        self.dealer_loop()

    @staticmethod
    def calc_eval_pts(player_ev, other_ev):
        return 0.5 * ((player_ev >= other_ev) + (player_ev > other_ev))

    @staticmethod
    def calc_profit(p_ev, o_ev, pot):
        p_ev_pts = BlackJack.calc_eval_pts(p_ev, o_ev)
        return pot * p_ev_pts

    @staticmethod
    def declare_winner(p_profit, d_profit):
        if p_profit > d_profit:
            print('player wins!')
        elif p_profit < d_profit:
            print('dealer wins')
        else:
            print('push')

    def eval_and_pay(self, d_ev, player):
        p_ev = self.eval_hard(player)
        print(f'{player.name} has {p_ev}')
        #
        pot = self.table.bets[player]
        p_profit = self.calc_profit(p_ev, d_ev, pot)
        d_profit = pot - p_profit
        #
        self.declare_winner(p_profit, d_profit)
        #
        player.cash += p_profit
        self.dealer.cash += d_profit
        self.table.bets[player] = 0
        print(f'now {player.name} has ${player.cash}.')

    def _wrap_ghost(self, ghost):
        p_name = ghost.name[:-1]
        p = self.table.find_player(p_name)
        p.cash += ghost.cash
        self.table.remove_player(ghost.name)
        self.ghost_players.remove(ghost)

    def _wrap_all_ghosts(self):
        for g in self.ghost_players:
            self._wrap_ghost(g)

    def eval_and_pay_all(self):
        d_ev = self.eval_hard(self.dealer)
        print(f'dealer has {d_ev}.')
        for p in self.table.players:
            if p == self.dealer:
                continue
            self.eval_and_pay(d_ev, p)
        self._wrap_all_ghosts()

    def clean_table(self):
        t = self.table
        for p in t.players:
            t.move_hand_to_scrap(p)
        if len(t.scrap) >= self.SCRAP_LIMIT:
            t.move_scrap_to_deck()
            print(f'shuffling cards...')
            t.pile.shuffle()

    def game(self):
        print('Collecting bets...')
        self.collect_bets()
        #
        print('Dealing cards to all players...')
        self.table.deal_cards_to_all(2)
        print(f'dealer showing {self.dealer.hand[0]}')
        #
        print('Now playing.')
        self.loop_all_players()
        #
        print('Now evaluating results and paying winners.')
        self.eval_and_pay_all()
        #
        print('Now cleaning table')
        self.clean_table()
        #
        print('Done with current round!')

    @staticmethod
    def eval_soft(player):
        h = player.hand
        res = 0
        for card in h:
            val = card.value
            res += 10 * (val >= 10) + val * (val < 10)
        return res

    @staticmethod
    def eval_hard(player):
        ev = BlackJack.eval_soft(player)
        if ev > 21:
            return 0
        if ev <= 11 and player.hand.find_value(1):
            ev += 10
        if ev == 21 and len(player.hand) == 2:
            ev = 99
        return ev

    def player_loop(self, player):
        p = player
        print(f"{p.name}'s turn.")
        while True:
            hard_ev = self.eval_hard(p)
            soft_ev = self.eval_soft(p)
            if not hard_ev:
                print('player busted')
                break
            print(f'{p.hand} {hard_ev}{f"/{soft_ev}" if hard_ev - soft_ev else ""}')
            ###
            st = 'H/S'
            if len(p.hand) == 2:
                st += '/D'
                if p.hand[0].value == p.hand[1].value:
                    st += '/s'
            st += '? '
            action = input(st)
            if action == 'S':
                break
            elif action == 'H':
                self.table.deal_card_to_player(p)
            elif action == 'D':
                self.collect_bet(p, self.table.bets[p] / 2)
                self.table.deal_card_to_player(p)
                break
            elif action == 's':
                tmp_p = self.table.add_player(p.name + '2', cash=0)
                self.ghost_players.append(tmp_p)
                self.collect_bet(tmp_p, self.table.bets[p] / 2, paying_player=p)
                self.table.move_card(p.hand, 1, tmp_p.hand)
                self.table.deal_card_to_player(p)
                self.player_loop(p)
                self.table.deal_card_to_player(tmp_p)
                break

            ###
            # if input('H/S? ') == 'S':
            #     break
            # self.table.deal_card_to_player(p)

    def dealer_loop(self):
        d = self.dealer
        while True:
            ev_hard = self.eval_hard(d)
            ev_soft = self.eval_soft(d)
            print(f'dealer hand: {d.hand} {ev_hard}{f"/{ev_soft}" if ev_hard - ev_soft else ""}')
            if not ev_hard:
                print('dealer busted')
                break
            if ev_hard < 17 or ev_soft == 7:
                print('dealer hits')
                self.table.deal_card_to_player(d)
                continue
            print('dealer stays')
            break


bj = BlackJack()
