import discord
from .voicevoxapi import voicevox
from discord.ext import commands
from discord import app_commands
from .lib import mng_speaker_id

# intents = discord.Intents.default()
# intents.voice_states = True
# bot = commands.Bot(command_prefix='!', intents=intents)

class MyCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.channel_id = None  # インスタンス変数として管理
        self.content = "hogehoge"  # 初期値を設定
        self.voicevox_instance = voicevox()  # インスタンスを作成
        self.mng_speaker_id = mng_speaker_id()
    
    Choice = discord.app_commands.Choice



    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if self.channel_id is None or message.channel.id != self.channel_id:
            print("Message not from target channel, ignoring.")
            return

        print(f"Received message: '{message.content}' in channel {message.channel.id}")
        print(f"Current channel_id: {self.channel_id}")


        self.content = message.content
        self.user_id = message.author.id
        self.server_id = message.guild.id

        print(self.user_id)
        print(self.server_id)


        voice_id = mng_speaker_id.get_voice_id(self.user_id, self.server_id)
        print(str(voice_id))

        if voice_id != None:
            self.voicevox_instance.hogehoge(self.content, voice_id)
        else:
            self.voicevox_instance.hogehoge(self.content, 3)
        print(f"Message from target channel: {message.content}")
        print("start")
        source = discord.FFmpegPCMAudio('voice/sample.wav')
        print("set path")
        message.guild.voice_client.play(source)
        print("play")
        print("remove and end")

    @app_commands.command(name='join', description='Say hello to the world!')
    async def join(self, interaction: discord.Interaction):
        self.channel_id = interaction.channel.id  # インスタンス変数に設定
        print(f"join command executed. channel_id set to: {self.channel_id}")
        print('Hello, World!' + str(self.channel_id))
        await interaction.response.send_message('接続しました', ephemeral=True)
        
        if isinstance(interaction.channel, discord.VoiceChannel):
            await interaction.channel.connect()
        elif interaction.user.voice is not None and interaction.user.voice.channel is not None:
            await interaction.user.voice.channel.connect()

    @app_commands.command(name='hoge', description='ほな')
    async def test(self, interaction: discord.Interaction):
        print(f"hoge command executed in channel {interaction.channel.id}")
        if interaction.user.voice is not None and interaction.user.voice.channel is not None:
            await interaction.guild.voice_client.disconnect()
            await interaction.response.send_message("ボイスチャンネルから離れました。", ephemeral=True)
            self.channel_id = None
        else:
            await interaction.response.send_message("ボイスチャンネルに接続していません。")

    @app_commands.command(name='play', description='さいせー')
    async def play(self, interaction: discord.Interaction):
        print("start")
        source = discord.FFmpegPCMAudio(f"voice/sample.wav")
        print("set path")
        await interaction.response.send_message("ボイスチ")
        print("send message")
        interaction.guild.voice_client.play(source)
        print("end")
