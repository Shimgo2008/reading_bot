import discord
from discord import app_commands
from discord.ext import commands, tasks
from .voicevoxapi import voicevox
from .lib import mng_speaker_id
from .cevio_net import CeVIO

# intents = discord.Intents.default()
# intents.voice_states = True
# bot = commands.Bot(command_prefix='!', intents=intents)

class MyCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.channel_id = None  # インスタンス変数として管理
        self.content = "hogehoge"  # 初期値を設定
        self.voicevox_instance = voicevox()
        self.mng_speaker_id = mng_speaker_id()
        self.cevio = CeVIO()
    
    Choice = discord.app_commands.Choice

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is None and after.channel is not None:
            # ユーザーがボイスチャンネルに参加したとき
            channel = after.channel
            if member != self.bot.user:
                display_name = member.display_name
                message = f"{display_name}さんが入室しました"
                print(message)
                self.voicevox_instance.hogehoge(message, 3)
                source = discord.FFmpegPCMAudio('voice/sample.wav')

                # 再生中でない場合に再生する
                if not channel.guild.voice_client.is_playing():
                    channel.guild.voice_client.play(source)

        elif before.channel is not None and after.channel is None:
            # ユーザーがボイスチャンネルから退出したとき
            channel = before.channel
            if member != self.bot.user:
                display_name = member.display_name
                message = f"{display_name}さんが退出しました"
                print(message)
                self.voicevox_instance.hogehoge(message, 3)
                source = discord.FFmpegPCMAudio('voice/sample.wav')

                # 再生中でない場合に再生する
                if not channel.guild.voice_client.is_playing():
                    channel.guild.voice_client.play(source)



    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author == self.bot.user or message.content[0] == ";" or message.content[0] == "；" or message.content[0:1] == "//":
            return

        if message.content == '@ピザ':
            await message.channel.send('https://www.pizza-la.co.jp/MenuList.aspx?ListId=Pizza',)


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

        if voice_id is None:
            print("voice_id is None, defaulting to Voicevox ID 3.")
            # self.voicevox_instance.hogehoge(self.content, 3)
            self.cevio.make_sound_CeVIO(self.content, "IA")
        elif voice_id == "IA":
            print("voice_id is IA")
            self.cevio.make_sound_CeVIO(self.content, voice_id)
        else:
            print(f"voice_id is {voice_id}")
            self.voicevox_instance.hogehoge(self.content, voice_id)
            # self.cevio.make_sound_CeVIO(self.content, "IA")

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
    
    @tasks.loop(seconds=5)
    async def check_voice_channel(self):
        if (not self.channel_id == None):
            for guild in self.bot.guilds:
                for vc in guild.voice_channels:
                    if vc.id == self.channel_id:
                        if len(vc.members) == 1 and vc.members[0].bot:  # ボットしかいない場合
                            await vc.guild.voice_client.disconnect()
                            # print('自動切断しました。')
                            self.channel_id = None

    @check_voice_channel.before_loop
    async def before_check_voice_channel(self):
        await self.bot.wait_until_ready()