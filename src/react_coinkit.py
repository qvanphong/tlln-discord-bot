import discord
from src.utils import env


class DiscordReactClient(discord.Client):
    async def on_message(self, message):
        if message.author is not None and message.guild is not None and message.channel is not None and hasattr(
                message.author, 'guild'):
            if message.author.guild.id == env.SERVER_ID and message.channel.id == 829403779513974824 \
                    and message.author.id == 546463922287411230:
                self.reaction_ = await message.add_reaction('💰')


client = DiscordReactClient()
client.run(env.TOKEN)
