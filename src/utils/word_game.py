import discord.client
import json
from src.model.session import Session
import definition
import time


class WordGame:
    # Word Game Session
    session = None

    # Game's responses loaded from Json
    responses = None

    # Discord's Client
    client = None

    # Session expire time
    expire_time = 300

    def __init__(self, client: discord.Client):
        self.client = client
        f = open(definition.get_path('assets/word_game_responses.json'), encoding="utf8")
        self.responses = json.load(f)

    async def check_expire_session(self, message):
        if self.session_created():
            current_time = time.time()
            if current_time - self.session.last_updated >= self.expire_time:
                self.session = None
                await self.send_message(message, "session_expire")

    # Create a game session, assign creator to session object
    async def create_session(self, message: discord.message):
        if self.session is not None:
            await self.send_message(message, "session_existed")
        else:
            if message.author is not None and message.author.display_name is not None:
                self._create_session(message.author)
                await self.send_message(message, "session_created", message.author.display_name)
            else:
                await self.send_message(message, "session_create_error")

    # Delete game session
    async def delete_session(self, message: discord.message):
        if self.is_from_creator(message):
            self.session = None
            await self.send_message(message, "session_deleted")

    # Reset the game session, which mean all value in variables will be back to default
    async def reset_session(self, message: discord.message):
        if self.is_from_creator(message):
            self._create_session(message.author)

    # Player join to the game, everytime player join, send a list players to them
    async def join(self, message: discord.message, player):
        if self.session_created() and self.session.is_started is False:
            if player is not None:
                self.session.add_player(player)
                await self.list_players(message)

                self.update_last_update()
            else:
                await self.send_message(message, "player_join_fail")
        else:
            await self.send_message(message, "no_session_to_join")

    async def quit(self, message, player):
        if self.session_created() and player is not None:
            if self.session.remove_player(player.id):
                await self.send_message(message, "quit", player.name)

    # Kick player out the game
    async def kick(self, message, player):
        if self.session_created() and self.is_from_creator(message) and player is not None:
            if self.session.remove_player(player.id):
                await self.send_message(message, "kicked", player.name)
                await self.list_players(message)

                self.update_last_update()
        else:
            await self.send_message(message, "kicked_not_found")

    # Set turn to the specific user, let that user answer again
    async def turn(self, message, player):
        if self.session_created() and self.is_from_creator(message) and self.session.is_started is True:
            if player.id in self.session.players_id:
                self.session.set_player_turn(player.id)
                self.session.previous_answer = ""
                await self.send_message(message, "answer_again", self.session.current_player_turn.name)

                self.update_last_update()

    # Start the game, will announce which player go first.
    async def start(self, message: discord.message):
        if self.session_created() and len(self.session.players) > 1:
            # Set first player to first turn (go first)
            self.session.is_started = True
            self.session.set_go_first_player()

            await self.send_message(message, "game_start")
            await self.announce_player_turn(message)

            self.update_last_update()
        elif len(self.session.players) <= 1:
            await self.send_message(message, "one_player_game_start")

    # Player response the answer,
    # check it with previous answer to find if the first word of this answer
    # is in the previous answer.
    # the answer argument must be pre-process (remove the !r part and to lower case)
    async def response_answer(self, message, answer):
        if self.is_from_player_on_turn(message):
            # If the previous_answer is empty, skip the validate
            if self.session.previous_answer == "":
                self.session.previous_answer = answer
                self.session.set_next_player_turn()
                await self.announce_player_turn(message)

                self.update_last_update()
            else:
                # Validate the previous answer and current answer
                split_answer = answer.split()
                split_previous_answer = self.session.previous_answer.split()
                last_word_from_previous = split_previous_answer[len(split_previous_answer) - 1]

                if split_answer[0] in last_word_from_previous:
                    self.session.previous_answer = answer
                    self.session.set_next_player_turn()
                    await self.announce_player_turn(message)

                    self.update_last_update()
                else:
                    await self.send_message(message, "no_match_word", last_word_from_previous)

    # Send message list of joined players
    async def list_players(self, message: discord.message):
        players_message = ">>> "
        for index, player in enumerate(self.session.players):
            players_message += "{}. **{}**\n".format(index + 1, player.name)
        await message.channel.send(players_message)
        self.update_last_update()

    # Create game session
    def _create_session(self, creator):
        self.session = Session(creator, time.time())

    # Send a message with specific message_type
    # check word_game_response.json, the key is message_type
    async def send_message(self, message, message_type, *args):
        if len(args) == 0:
            await message.channel.send(">>> " + self.responses[message_type])
        else:
            await message.channel.send(">>> " + self.responses[message_type].format(*args))

    async def announce_player_turn(self, message):
        await self.send_message(message, "turn", self.session.previous_answer, self.session.current_player_turn.name)

    def is_from_creator(self, message):
        return self.session_created() and self.session.creator.id == message.author.id

    def is_from_player_on_turn(self, message):
        return self.session_created() and self.session.current_player_turn.id == message.author.id

    def session_created(self):
        return self.session is not None

    # Update last update time
    def update_last_update(self):
        self.session.last_updated = time.time()
