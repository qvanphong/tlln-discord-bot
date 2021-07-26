import discord
from src.utils import env, word_game
import re


class WordGameClient(discord.Client):
    word_game = None
    response_regex = r"^!r [ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂưăạảấầẩẫậắằẳẵặẹẻẽềềểỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹA-Za-z ]*$"

    async def on_ready(self):
        self.word_game = word_game.WordGame(self)

    async def on_message(self, message):
        if message.author is not None and message.guild is not None and message.channel is not None and hasattr(
                message.author, 'guild') and message.channel.id == env.ARK_CHANNEL:
            message_content = message.content.lower()

            if message_content == "!luatchoi":
                await self.word_game.send_message(message, "rule")
                return

            if message_content == "!huongdan":
                await self.word_game.send_message(message, "tutorial")
                return

            # Create game session command
            if message_content == "!create":
                await self.word_game.create_session(message)

            # Start word game command
            if message_content == "!start":
                await self.word_game.start(message)

            # Reset the game, delete all players that joined the queue
            if message_content == "!reset":
                await self.word_game.reset_session(message)

            # Game session remove.
            if message_content == "!delete":
                await self.word_game.delete_session(message)

            # List all joined players
            if message_content == "!list":
                await self.word_game.list_players(message)

            # Player join the game.
            if message_content == "!join":
                profile = await self.fetch_user_profile(message.author.id)
                await self.word_game.join(message, profile.user)

            # Player quit the game
            if message_content == "!quit":
                profile = await self.fetch_user_profile(message.author.id)
                await self.word_game.quit(message, profile.user)

            # Response the next word.
            if "!r " in message_content:
                matches = re.search(self.response_regex, message_content.strip(), re.IGNORECASE)
                if matches is not None:
                    await self.word_game.response_answer(message, message_content.split("!r ")[1].strip())

            # Kick someone out the queue
            if "!kick " in message_content:
                if len(message.mentions) > 0:
                    profile = await self.fetch_user_profile(message.mentions[0].id)
                    await self.word_game.kick(message, profile)

            # Back to specific user to play.
            if "!turn " in message_content:
                if len(message.mentions) > 0:
                    profile = await self.fetch_user_profile(message.mentions[0].id)
                    await self.word_game.turn(message, profile)



# Run the game
WordGameClient().run(env.TOKEN)
