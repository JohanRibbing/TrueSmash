import trueskill as ts
import random


class Player:
    def __init__(self, dct):
        self.name = dct['name']
        self.mu_singles = dct['mu_singles']
        self.sigma_singles = dct['sigma_singles']
        self.mu_doubles = dct['mu_doubles']
        self.sigma_doubles = dct['sigma_doubles']
    
    def get_singles_rating(self):
        return ts.Rating(mu=self.mu_singles,
                      sigma=self.sigma_singles)

    def get_doubles_rating(self):
        return ts.Rating(mu=self.mu_doubles,
                      sigma=self.sigma_doubles)

    def get_singles_trueskill(self):
        return self.mu_singles - 3*self.sigma_singles

    def get_doubles_trueskill(self):
        return self.mu_doubles - 3*self.sigma_doubles

class Database:
    def __init__(self, players_json):
        self.players = [Player(p) for p in players_json['players']]
    
    def add_player(self, name):
        new_player_dict = dict(name=name,
                            mu_singles=25, sigma_singles=25/3,
                            mu_doubles=25, sigma_doubles=25/3)

        self.players.append(Player(new_player_dict))
        print('Added ', name)
        return True

    def delete_player(self, name):
        removed = ''
        for i, p in enumerate(self.players):
            if p.name == name:
                removed = self.players.pop(i)
                print('Removed ', removed.name)
        if removed == '':
            print('No such player')
            return False
        else:
            return True

    def reset_ratings(self):
        names = [p.name for p in self.players]
        self.players = []
        for name in names:
            self.add_player(name)
        return True

    def play_match_singles(self):
        if len(self.players) < 2:
            print('Not enough players')
            return False

        p1, p2 = random.sample(self.players, 2)
        vs_dict = {p1.name: p1, p2.name: p2}
        print(p1.name, ' vs ', p2.name)
        print('Who won?')
        winner_name = ''
        while winner_name != p1.name and winner_name != p2.name:
            print('Input player tag:')
            winner_name = input()
        winner = vs_dict.pop(winner_name)
        loser = list(vs_dict.values())[0]
        w_rating = winner.get_singles_rating()
        l_rating = loser.get_singles_rating()
        w_rating, l_rating = ts.rate_1vs1(w_rating, l_rating,
                env=ts.TrueSkill(draw_probability=0.0))

        winner.mu_singles = w_rating.mu
        winner.sigma_singles = w_rating.sigma
        loser.mu_singles = l_rating.mu
        loser.sigma_singles = l_rating.sigma
        print('Ratings updated')
        return True

    def play_match_doubles(self):
        if len(self.players) < 4:
            print('Not enough players')
            return False

        # t1p1, t1p2, t2p1, t2p2
        lineup = random.sample(self.players, 4)
        ratings = [p.get_doubles_rating() for p in lineup]
        print(f'(Blue team: {lineup[0].name} and {lineup[1].name})',
                ' vs ',
              f'(Red team: {lineup[2].name} and {lineup[3].name})')
        print('Who won?')
        winner_team = ''
        while winner_team != 'blue' and winner_team != 'red':
            print('Input blue or red:')
            winner_team = input()

        rating_groups = [
                (ratings[0], ratings[1]),
                (ratings[2], ratings[3])
                        ]
        rated_rating_groups = ts.TrueSkill(draw_probability=0.0).rate(
                rating_groups,
                ranks=[
                       int('blue'!=winner_team),
                       int('red'!=winner_team)
                      ]
                                                                  )
        new_ratings = []
        for team in (0, 1):
            for player in (0, 1):
                new_ratings.append(rated_rating_groups[team][player])

        for i, p in enumerate(lineup):
            p.mu_doubles = new_ratings[i].mu
            p.sigma_doubles = new_ratings[i].sigma

        print('Ratings updated')
        return True

    def get_ladder_singles(self):
        sorted_players = sorted(self.players,
                key=lambda x: x.get_singles_trueskill(),
                reverse=True)
        return (
                [p.name
                        for p in sorted_players],
                [round(p.get_singles_trueskill(), 3)
                       for p in sorted_players]
               )

    def get_ladder_doubles(self):
        sorted_players = sorted(self.players,
                key=lambda x: x.get_doubles_trueskill(),
                reverse=True)
        return (
                [p.name
                        for p in sorted_players],
                [round(p.get_doubles_trueskill(), 3)
                        for p in sorted_players]
               )



