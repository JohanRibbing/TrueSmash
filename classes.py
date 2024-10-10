class Player:
    def __init__(self, dct):
        self.name = dct['name']
        self.mu_singles = dct['mu_singles']
        self.sigma_singles = dct['sigma_singles']
        self.mu_doubles = dct['mu_doubles']
        self.sigma_doubles = dct['sigma_doubles']

class Database:
    def __init__(self, players_json):
        self.players = [Player(p) for p in players_json['players']]
    
    def add_player(self, name):
        new_player_dict = dict(name=name,
                            mu_singles=25, sigma_singles=25/3,
                            mu_doubles=25, sigma_doubles=25/3)

        self.players.append(Player(new_player_dict))
        print('Added ', name)

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
