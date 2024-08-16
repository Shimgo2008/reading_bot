import discord
from discord.ext import commands
from discord import app_commands

class MyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = None  # インスタンス変数として管理

    @commands.Cog.listener()
    async def on_message(self, message):
        print(f"Received message: '{message.content}' in channel {message.channel.id}")
        print(f"Current channel_id: {self.channel_id}")
        
        if message.author == self.bot.user:
            return

        if self.channel_id is None or message.channel.id != self.channel_id:
            print("Message not from target channel, ignoring.")
            return

        print(f"Message from target channel: {message.content}")

    @app_commands.command(name='join', description='Say hello to the world!')
    async def join(self, interaction: discord.Interaction):
        self.channel_id = interaction.channel.id  # インスタンス変数に設定
        print(f"join command executed. channel_id set to: {self.channel_id}")
        await interaction.response.send_message('Hello, World!' + str(self.channel_id))
        
        if isinstance(interaction.channel, discord.VoiceChannel):
            await interaction.channel.connect()
        elif interaction.user.voice is not None and interaction.user.voice.channel is not None:
            await interaction.user.voice.channel.connect()

    @app_commands.command(name='hoge', description='ほな')
    async def test(self, interaction: discord.Interaction):
        print(f"hoge command executed in channel {interaction.channel.id}")
        if interaction.user.voice is not None and interaction.user.voice.channel is not None:
            await interaction.guild.voice_client.disconnect()
            await interaction.response.send_message("ボイスチャンネルから離れました。")
        else:
            await interaction.response.send_message("ボイスチャンネルに接続していません。")
