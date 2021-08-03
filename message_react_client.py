import discord
import re
from src.utils.responder import Responder
import emojis
from src.repository import reaction_repository
from src.utils import env


async def send_success_message(message):
    await message.channel.send('>>> Đã bật auto react cho **{}** <:OK:778028306699124797>, gõ **!stop** để dừng'.format(
        message.author.display_name))


async def send_stop_message(message):
    await message.channel.send(
        '>>> Đã tắt auto react cho **{}** <:OK:778028306699124797>'.format(message.author.display_name))


async def send_fail_message(message):
    await message.channel.send(
        '>>> Sai cú pháp hoặc không tìm thấy Emoji (Chỉ dùng emoji tĩnh trong server và emoji mặc định).')


class DiscordReactClient(discord.Client):
    cs = None
    server_emoji = []

    async def on_ready(self):
        self.cs = Responder(client)

        # Fetch guild's emoji, animated emoji is not allowed.
        for guild in client.guilds:
            if guild.id == env.SERVER_ID:
                for e in guild.emojis:
                    if e.animated is False:
                        self.server_emoji.append(str(e))

    async def on_message(self, message):
        if message.author is not None \
                and message.guild is not None \
                and message.channel is not None \
                and hasattr(message.author, 'guild') \
                and message.author.guild.id == env.SERVER_ID \
                and message.channel.id == 829403779513974824:

            # Check if message have !react command
            if "!react" in message.content.lower():
                emoji_list = []
                split_message = message.content.split("!react ")
                if len(split_message) >= 2:
                    encoded_emojis = split_message[1].split()
                    for encoded_emoji in encoded_emojis[0:2]:
                        match = re.search(self.cs.emoji_regex, encoded_emoji, re.IGNORECASE)

                        # If server emoji found and it must in server, then insert it to DB
                        if match is not None and match.group() in self.server_emoji:
                            emoji_list.append(match.group())

                        # If it's not server emoji, check if it's a unicode emoji
                        else:
                            decoded_emoji = emojis.decode(encoded_emoji.strip())
                            if decoded_emoji[0] == ":" and decoded_emoji[len(decoded_emoji) - 1] == ":":
                                emoji_list.append(encoded_emoji.strip())

                    if len(emoji_list) > 0:
                        reaction_repository.insert_to_db(message.author.id, emoji_list)
                        await send_success_message(message)
                        return

                await send_fail_message(message)
                return

            elif "!stop" == message.content.lower():
                reaction_repository.delete_author(message.author.id)
                await send_stop_message(message)
                return
            else:
                r = reaction_repository.get_author_emoji(message.author.id)
                if r is not None:
                    for emoji in r["emoji"]:
                        await message.add_reaction(emoji)


client = DiscordReactClient()
client.run(env.TOKEN)
