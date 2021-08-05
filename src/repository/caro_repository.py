from tinydb import TinyDB, Query
from functools import cmp_to_key
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
    def comparator(e1, e2):
        if e1["win"] > e2["win"]:
            return 1
        elif e1["win"] < e2["win"]:
            return -1
        else:
            if e1["win"] == e2["win"]:
                if e1["lose"] > e2["lose"]:
                    return -1
                elif e1["lose"] < e2["lose"]:
                    return 1
                else:
                    return 0

    result = db.all()
    return sorted(result, key=cmp_to_key(comparator), reverse=True)[0:10]

