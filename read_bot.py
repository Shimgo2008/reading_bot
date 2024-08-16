import discord
from discord.ext import commands
from discord import app_commands 
import asyncio
import os
import settings
import subprocess
# import ffmpeg
# from voice_generator import creat_WAV

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)
tree = client.tree
# 既存のコマンドツリーが存在しない場合のみ新たに作成
if not hasattr(client, 'tree'):
    tree = app_commands.CommandTree(client)
    print("generate tree")

TOKEN = settings.BOT_TOKEN

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

@client.event
async def on_ready():
    print('ログインしました') 
    new_activity = f"テスト" 
    await client.change_presence(activity=discord.Game(new_activity))  
    await tree.sync()


@client.tree.command(name='join', description='Say hello to the world!') 
async def join(interaction: discord.Interaction): 
    channel = interaction.channel
    global channel_id
    channel_id = channel.id
    await interaction.response.send_message('Hello, World!' + str(channel.id))
    
    if isinstance(channel, discord.VoiceChannel):
        await channel.connect()
    elif interaction.user.voice is not None and interaction.user.voice.channel is not None:
        await interaction.user.voice.channel.connect()


@client.tree.command(name='hoge', description='ほな')
async def test(interaction: discord.Interaction):
    if interaction.user.voice is not None and interaction.user.voice.channel is not None:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("ボイスチャンネルから離れました。")
    else:
        await interaction.response.send_message("ボイスチャンネルに接続していません。")

client.run(TOKEN)