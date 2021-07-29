from tinydb import TinyDB, Query
import definition

db = TinyDB(definition.get_path('db/caro_leaderboard.json'))
Player = Query()


def save_score(player, win_or_lose):
    existed_score = db.get(Player.id == player.id)
    if existed_score is None:
        if win_or_lose == "win":
            return db.insert({'name': player.name, 'id': player.id, 'win': 1, 'lose': 0})
        else:
            return db.insert({'name': player.name, 'id': player.id, 'win': 0, 'lose': 1})
    else:
        if win_or_lose == "win":
            return db.update({'win': existed_score["win"]+1}, Player.id == player.id)
        else:
            return db.update({'lose': existed_score["lose"] + 1}, Player.id == player.id)


def get_all_score():
    def win(e):
        return e["win"]

    result = db.all()[0:10]
    result.sort(reverse=True, key=win)
    return result
