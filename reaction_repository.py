from tinydb import TinyDB, Query
from tinydb.operations import delete

db = TinyDB('db/reaction.json')
reaction_query = Query()


def insert_to_db(author, emojis):
    if db.get(reaction_query.author == author) is None:
        return db.insert({'author': author, 'emoji': emojis})
    else:
        return db.update({'author': author, 'emoji': emojis}, reaction_query.author == author)


def get_author_emoji(author):
    return db.get(reaction_query.author == author)


def delete_author(author):
    return db.update(delete('author'), reaction_query.author == author)


def init_fetch():
    return db.all()
