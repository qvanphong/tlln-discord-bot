import discord
import env
import re
from command_sender import CommandSender
import emojis
import reaction_db


class DiscordReactClient(discord.Client):
    cs = None
    server_emoji = []
    cached = None

    async def on_ready(self):
        print("Reaction Emoji ready")
        self.cs = CommandSender(client)
        self.cached = reaction_db.init_fetch()
        for guild in client.guilds:
            if guild.id == env.SERVER_ID:
                for e in guild.emojis:
                    self.server_emoji.append(str(e))

    async def on_message(self, message):
        if message.author is not None and message.guild is not None and message.channel is not None and hasattr(
                message.author, 'guild'):
            if message.author.guild.id == env.SERVER_ID and message.channel.name == 'ark':

                # Check if message have !react command
                if "!react" in message.content.lower():
                    emojiz = []
                    split_message = message.content.split("!react ")
                    if len(split_message) >= 2:
                        encoded_emojis = split_message[1].split()
                        for encoded_emoji in encoded_emojis[0:2]:
                            match = re.search(self.cs.emoji_regex, encoded_emoji, re.IGNORECASE)
                            if match is not None:
                                emojiz.append(match.group())
                            else:
                                decoded_emoji = emojis.decode(encoded_emoji.strip())
                                if decoded_emoji[0] == ":" and decoded_emoji[len(decoded_emoji) - 1] == ":":
                                    emojiz.append(encoded_emoji.strip())

                        if len(emojiz) > 0:
                            reaction_db.insert_to_db(message.author.id, emojiz)
                            await self.send_success_message(message)
                            return

                    await self.send_fail_message(message)
                    return

                elif "!stop" == message.content.lower():
                    reaction_db.delete_author(message.author.id)
                    return
                else:
                    r = reaction_db.get_author_emoji(message.author.id)
                    if r is not None:
                        for emojiz in r["emoji"]:
                            await message.add_reaction(emojiz)

    async def send_success_message(self, message):
        await message.channel.send('>>> {} <:OK:778028306699124797>, gõ **!stop** để dừng'.format(message.author.display_name))

    async def send_fail_message(self, message):
        await message.channel.send(
            '>>> Sai cú pháp hoặc không tìm thấy Emoji (Chỉ dùng emoji tĩnh trong server và emoji mặc định).')


client = DiscordReactClient()
client.run(env.TOKEN)
