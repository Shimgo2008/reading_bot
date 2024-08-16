import discord
from discord.ext import commands
from discord import app_commands

channel_id = None

class MyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if message.channel.id != channel_id:
            return

        print(message.content)
        print(f"Message from target channel: {message.content}")

    @app_commands.command(name='join', description='Say hello to the world!')
    async def join(self, interaction: discord.Interaction):
        global channel_id
        channel = interaction.channel
        channel_id = channel.id
        await interaction.response.send_message('Hello, World!' + str(channel.id))
        
        if isinstance(channel, discord.VoiceChannel):
            await channel.connect()
        elif interaction.user.voice is not None and interaction.user.voice.channel is not None:
            await interaction.user.voice.channel.connect()

    @app_commands.command(name='hoge', description='ほな')
    async def test(self, interaction: discord.Interaction):
        if interaction.user.voice is not None and interaction.user.voice.channel is not None:
            await interaction.guild.voice_client.disconnect()
            await interaction.response.send_message("ボイスチャンネルから離れました。")
        else:
            await interaction.response.send_message("ボイスチャンネルに接続していません。")
