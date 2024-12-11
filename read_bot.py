import discord # わすれないでね❤
from discord.ext import commands
from discord import app_commands
import asyncio
import settings
from cogs.conect_vc import MyCog
from cogs.lib import mng_speaker_id

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


@client.tree.command(name="set_speaker", description="喋る声を変えます")
@app_commands.describe(声="helloworld")
@app_commands.choices(声=[
    discord.app_commands.Choice(name="無し", value="No"),

    discord.app_commands.Choice(name="IA姉", value="IA"),

    discord.app_commands.Choice(name="四国めたん", value="2"),
    discord.app_commands.Choice(name="あまあま四国めたん", value="0"),
    discord.app_commands.Choice(name="ツンツン四国めたん", value="6"),
    discord.app_commands.Choice(name="セクシー四国めたん", value="4"),

    discord.app_commands.Choice(name="ずんだもん", value="3"),
    discord.app_commands.Choice(name="あまあまずんだもん", value="1"),
    discord.app_commands.Choice(name="ツンツンずんだもん", value="7"),
    discord.app_commands.Choice(name="セクシーずんだもん", value="5"),
    discord.app_commands.Choice(name="ささやきずんだもん", value="22"),
    discord.app_commands.Choice(name="へろへろずんだもん", value="75"),

    discord.app_commands.Choice(name="春日部つむぎ", value="8"),

    discord.app_commands.Choice(name="小夜/SAYO", value="46"),

    discord.app_commands.Choice(name="中国うさぎ", value="61"),
    discord.app_commands.Choice(name="おどろき中国うさぎ", value="62"),
    discord.app_commands.Choice(name="こわがり中国うさぎ", value="63"),
    discord.app_commands.Choice(name="へろへろ中国うさぎ", value="64"),

    discord.app_commands.Choice(name="タイプT", value="49"),
    discord.app_commands.Choice(name="楽々タイプT", value="50"),
    discord.app_commands.Choice(name="怖がりタイプT", value="51"),
    discord.app_commands.Choice(name="ささやきタイプT", value="52"),
])
async def set_speaker(interaction: discord.Interaction, 声: discord.app_commands.Choice[str] = "IA姉"):
    name = 声.name
    value = 声.value
    server_id = interaction.guild.id
    user_id = interaction.user.id
    print(f"server id is {server_id}")
    print(f"user id is {user_id}")
    print(f"value is {value}")

    await interaction.response.send_message(f"あなたの音声を{name}に設定しました", ephemeral=True)
    mng_speaker_id.save_data(user_id, value, server_id)
    print(mng_speaker_id.load_data(server_id, filename=None))


# asyncio.run() を使用して非同期関数を実行
asyncio.run(setup())