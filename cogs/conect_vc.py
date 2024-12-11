import discord
from discord import app_commands
from discord.ext import commands, tasks

import asyncio
import logging
import json
from pathlib import Path

from .voicevoxapi import voicevox
from .lib import mng_speaker_id, mng_dict
from .cevio_net import CeVIO
from .jiho import jiho  # Jihoクラスをインポート

# ログの設定
logging.basicConfig(
    level=logging.INFO,  # 既存パッケージのデバッグログを抑える
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# モジュール専用ロガー
logger = logging.getLogger(__name__)  # モジュール名をロガー名として使用

class MyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_ids = {}  # ギルド（サーバー）ごとのチャンネルIDを記録
        self.voice_connections = {}  # ギルドごとのVoiceClientを記録
        self.voicevox_instance = voicevox()
        self.mng_speaker_id = mng_speaker_id()
        self.cevio = CeVIO()
        self.jiho = jiho(self.voice_connections)
        self.dict = mng_dict()
        

        # タスクの初期化
        self.cleanup_voice_files.start()
        self.jiho_task.start()
        self.auto_disconnect.start()
        logger.info("MyCog initialized.")

    @tasks.loop(minutes=10)
    async def cleanup_voice_files(self):
        logger.info("Running cleanup_voice_files task.")
        for file in Path('./voice').glob('*.wav'):
            file.unlink()
            logger.info(f"Deleted old file: {file}")

    @tasks.loop(seconds=1)
    async def jiho_task(self):
        await self.jiho.jiho_task()

    @jiho_task.before_loop
    async def before_jiho_task(self):
        logger.info("Waiting for bot to be ready before jiho task.")
        await self.bot.wait_until_ready()

    @tasks.loop(seconds=10)
    async def auto_disconnect(self):
        logger.info("Running auto_disconnect task.")
        for guild_id, vc in list(self.voice_connections.items()):
            if len(vc.channel.members) == 1:  # ボットのみの場合
                logger.info(f"Voice channel in guild {guild_id} is empty. Disconnecting.")
                await vc.disconnect()
                del self.voice_connections[guild_id]

    @auto_disconnect.before_loop
    async def before_auto_disconnect(self):
        logger.info("Waiting for bot to be ready before auto_disconnect task.")
        await self.bot.wait_until_ready()

    @cleanup_voice_files.before_loop
    async def before_cleanup_voice_files(self):
        logger.info("Waiting for bot to be ready before cleanup task.")
        await self.bot.wait_until_ready()

    async def process_message(self, message):
        logger.debug(f"Processing message: {message.content} from {message.author}")

        # メッセージがDMまたは無関係なチャンネルの場合は無視
        if message.guild is None:
            logger.warning("Message does not belong to a guild. Ignoring.")
            return

        if message.author.bot:
            logger.debug("Message is from bot itself. Ignoring.")
            return

        if message.content == '@ピザ':
            await message.channel.send('https://www.pizza-la.co.jp/MenuList.aspx?ListId=Pizza',)
            if message.author.voice.channel != None:
                source = discord.FFmpegPCMAudio('protect_voice_data/piza.wav')
            if message.guild.voice_client:
                if not message.guild.voice_client.is_playing():
                    logger.debug("Playing audio file.")
                    message.guild.voice_client.play(source)
                else:
                    logger.warning("Client is already playing, waiting for it to finish.")
                    while message.guild.voice_client.is_playing():
                        await asyncio.sleep(0.5)
                    logger.debug("Replaying audio after waiting.")
                    message.guild.voice_client.play(source)
                print("hoge")
                return
            return

        guild_id = message.guild.id
        if guild_id not in self.channel_ids or message.channel.id != self.channel_ids[guild_id]:
            logger.info(f"Message channel ({message.channel.id}) is not the configured channel for guild {guild_id}. Ignoring.")
            return

        if message.content.startswith((";", "；", "//")):
            logger.debug("Message starts with ignored prefix. Skipping.")
            return

        self.content = message.content
        self.user_id = message.author.id
        self.server_id = message.guild.id
        self.message_hash = hash(message)

        voice_id = self.mng_speaker_id.get_voice_id(self.user_id, self.server_id)
        logger.debug(f"Voice ID for user {self.user_id}: {voice_id}")

        try:
            with open(f'server/{self.server_id}/phonetic_dict.json', 'r', encoding='utf-8') as f:
                dict_json = json.load(f)
            dict_json = dict(dict_json)
            logger.info(f"current dict is {dict_json}")

            for key, value in dict_json.items():
                self.content = self.content.replace(key, value)

        except Exception:
            logger.error("辞書がないお")



        try:
            match voice_id:
                case "No":
                    return
                case None:
                    # self.voicevox_instance.hogehoge(self.content, "3", self.message_hash)
                    self.cevio.make_sound_CeVIO(self.content, voice_id, f"{self.message_hash}.wav")
                case "IA":
                    logger.info("Using CeVIO with IA voice.")
                    self.cevio.make_sound_CeVIO(self.content, voice_id, f"{self.message_hash}.wav")
                case _:
                    logger.info("Using Voicevox for synthesis.")
                    self.voicevox_instance.hogehoge(self.content, voice_id, self.message_hash)

            source = discord.FFmpegPCMAudio(f'voice/{self.message_hash}.wav')
            if message.guild.voice_client:
                if not message.guild.voice_client.is_playing():
                    logger.debug("Playing audio file.")
                    message.guild.voice_client.play(source)
                else:
                    logger.warning("Client is already playing, waiting for it to finish.")

                    logger.debug("Replaying audio after waiting.")
                    message.guild.voice_client.play(source)
            else:
                logger.warning("No active voice client.")
        except Exception as e:
            logger.error(f"Error in process_message: {e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        logger.debug(f"Received message: {message.content}")
        asyncio.create_task(self.process_message(message))

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        guild_id = member.guild.id

        # 1. 設定されていない場合は無視
        if guild_id not in self.channel_ids:
            return

        target_channel_id = self.channel_ids[guild_id]

        # 入室処理
        if before.channel is None and after.channel is not None:
            if after.channel.id != target_channel_id:
                return  # 対象外チャンネルは無視
            if member != self.bot.user:  # 自分自身のイベントは無視
                display_name = member.display_name
                message = f"{display_name}さんが入室しました"
                logger.info(message)

                try:
                    # 音声ファイルを生成
                    self.cevio.make_sound_CeVIO(str(message), "IA", f"{hash(message)}.wav")
                    source = discord.FFmpegPCMAudio(f'voice/{hash(message)}.wav')

                    # ボイスクライアントが接続されている場合
                    if after.channel.guild.voice_client:
                        if not after.channel.guild.voice_client.is_playing():
                            logger.debug("Playing audio file.")
                            after.channel.guild.voice_client.play(source)
                        else:
                            logger.warning("Client is already playing, waiting for it to finish.")
                            while after.channel.guild.voice_client.is_playing():
                                await asyncio.sleep(0.5)
                            logger.debug("Replaying audio after waiting.")
                            after.channel.guild.voice_client.play(source)
                    else:
                        logger.warning("No active voice client.")
                except Exception as e:
                    logger.error(f"Error during join message processing: {e}")

        elif before.channel is not None and after.channel is None:
            if before.channel.id != target_channel_id:
                return  # 対象外チャンネルは無視
            if member != self.bot.user:
                display_name = member.display_name
                message = f"{display_name}さんが退出しました"
                logger.info(message)

                try:
                    self.cevio.make_sound_CeVIO(str(message), "IA", f"{hash(message)}.wav")
                    source = discord.FFmpegPCMAudio(f'voice/{hash(message)}.wav')

                    # ボイスクライアントが接続されている場合
                    if before.channel.guild.voice_client:
                        if not before.channel.guild.voice_client.is_playing():
                            logger.debug("Playing audio file.")
                            before.channel.guild.voice_client.play(source)
                        else:
                            logger.warning("Client is already playing, waiting for it to finish.")
                            while before.channel.guild.voice_client.is_playing():
                                await asyncio.sleep(0.5)
                            logger.debug("Replaying audio after waiting.")
                            before.channel.guild.voice_client.play(source)
                    else:
                        logger.warning("No active voice client.")
                except Exception as e:
                    logger.error(f"Error during leave message processing: {e}")

    @app_commands.command(name='join', description='ボイスチャンネルに参加')
    async def join(self, interaction: discord.Interaction):
        logger.info("join command received.")
        guild_id = interaction.guild.id
        self.channel_ids[guild_id] = interaction.channel.id  # サーバーごとのチャンネルIDを記録

        if guild_id in self.voice_connections:
            logger.warning(f"Already connected to a voice channel in guild {guild_id}.")
            await interaction.response.send_message("既に接続しています。", ephemeral=True)
            return

        if interaction.user.voice and interaction.user.voice.channel:
            voice_channel = interaction.user.voice.channel
            logger.info(f"User {interaction.user} is in voice channel {voice_channel}. Attempting to connect.")
            try:
                vc = await voice_channel.connect()
                self.voice_connections[guild_id] = vc
                logger.info(f"Successfully connected to voice channel {voice_channel}.")
                await interaction.response.send_message("接続しました。", ephemeral=True)
            except Exception as e:
                logger.error(f"Error connecting to voice channel in guild {guild_id}: {e}")
                await interaction.response.send_message("接続できませんでした。", ephemeral=True)
        else:
            logger.warning(f"User {interaction.user} is not in a voice channel.")
            await interaction.response.send_message("ボイスチャンネルに接続できませんでした。", ephemeral=True)

    @app_commands.command(name='leave', description='ボイスチャンネルから離れる')
    async def leave(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        if guild_id in self.voice_connections:
            vc = self.voice_connections.pop(guild_id)
            await vc.disconnect()
            logger.info(f"Disconnected from voice channel in guild {guild_id}.")
            await interaction.response.send_message("切断しました。", ephemeral=True)
        else:
            logger.warning(f"No active voice connection in guild {guild_id}.")
            await interaction.response.send_message("ボイスチャンネルに接続していません。", ephemeral=True)
    @app_commands.choices(何時=[
        discord.app_commands.Choice(name="0時", value="0"),
        discord.app_commands.Choice(name="1時", value="1"),
        discord.app_commands.Choice(name="2時", value="2"),
    ])
    @app_commands.command(name="じほー", description="じほー")
    async def jiho(self, interaction: discord.Interaction, 何時:str):
        print("start")
        source = discord.FFmpegPCMAudio(f"protect_voice_data/niconico_ziho_{何時}h.wav")
        print("set path")
        await interaction.response.send_message(f"{何時}時のじほー", ephemeral=True)
        await interaction.guild.voice_client.play(source)
        print("end")

    @app_commands.command(name="dictionary_add", description="サーバー辞書に追加")
    async def dictionary_add(self, interaction: discord.Interaction, 単語: str, 読み:str):
        logger.info("run disctionary add")
        add_log = self.dict.save_dic(interaction.guild_id, 単語, 読み)
        logger.info(add_log)
        await interaction.response.send_message(str(add_log))

    @app_commands.command(name="dictionary_remove", description="サーバー辞書から削除")
    async def dictionary_remove(self, interaction: discord.Interaction, 単語: str):
        logger.info("run disctionary remove")
        remove_log = self.dict.remove_dict(interaction.guild_id, 単語)
        logger.info(remove_log)
        await interaction.response.send_message(remove_log)

    @app_commands.command(name="dictionary_list", description="サーバー辞書を参照")
    async def dictionary_list(self, interaction: discord.Interaction, ):
        logger.info("run disctionary list")
        list_log = self.dict.list_dict(interaction.guild_id)
        await interaction.response.send_message(list_log)