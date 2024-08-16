import discord
from discord.ext import commands
import asyncio
import settings
from cogs.my_cog import MyCog

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = commands.Bot(command_prefix="!", intents=intents)

TOKEN = settings.BOT_TOKEN

@client.event
async def on_ready():
    print('ログインしました')
    new_activity = f"テスト" 
    await client.change_presence(activity=discord.Game(new_activity))
    await client.tree.sync()

async def setup():
    await client.add_cog(MyCog(client))
    await client.start(TOKEN)

# asyncio.run() を使用して非同期関数を実行
asyncio.run(setup())