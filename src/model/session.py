class Session:
    creator = ""
    players = []
    players_id = []
    current_player_turn = None
    previous_answer = ""
    is_started = False
    last_updated = None

    def __init__(self, creator, create_time):
        self.creator = creator
        self.add_player(creator)
        self.last_updated = create_time

    def add_player(self, player):
        if self._add_player_id(player.id):
            self.players.append(player)
            return True
        return False

    def remove_player(self, player_id):
        if player_id in self.players_id:
            self.players_id.remove(player_id)
            self.players = [player for player in self.players if player.id != player_id]
            return True
        return False

    # Due to selfbot problem, I can't get some user's display_name
    # So I will use players_id to save their ID and save their profile's name
    # This will solve the problem that use change his name while playing
    def _add_player_id(self, player_id):
        if player_id not in self.players_id:
            self.players_id.append(player_id)
            return True
        return False

    def set_go_first_player(self):
        self.current_player_turn = self.players[0]

    def get_current_player_name(self):
        if self.current_player_turn is not None:
            return self.current_player_turn.display_name
        return None

    def set_next_player_turn(self):
        index = self.players.index(self.current_player_turn)
        if index + 1 >= len(self.players):
            self.current_player_turn = self.players[0]
        else:
            self.current_player_turn = self.players[index + 1]

    def set_player_turn(self, id):
        for player in self.players:
            if player.id == id:
                self.current_player_turn = player
                return
