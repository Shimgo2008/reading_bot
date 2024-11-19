import discord
from discord import app_commands
from discord.ext import commands, tasks
import asyncio
import time
from pathlib import Path
import logging
from .voicevoxapi import voicevox
from .lib import mng_speaker_id
from .cevio_net import CeVIO

# ログの設定
logging.basicConfig(
    level=logging.INFO,  # 既存パッケージのデバッグログを抑える
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# conect_vc専用ロガーを作成
specific_logger = logging.getLogger("conect_vc")
specific_logger.setLevel(logging.DEBUG)  # DEBUGレベルに設定

# 既存パッケージのログを抑制（例：discordのログ）
logging.getLogger("discord").setLevel(logging.WARNING)
logging.getLogger("discord.ext").setLevel(logging.WARNING)

# conect_vc専用のハンドラー（ストリーム）を追加
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s [%(name)s] [%(levelname)s] %(message)s")
handler.setFormatter(formatter)
specific_logger.addHandler(handler)

# モジュールごとのロガーを作成
logger = logging.getLogger(__name__)  # モジュール名を使うことで識別可能なロガーを作成


class MyCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.channel_id = None
        self.voice_connections = {}
        self.voicevox_instance = voicevox()
        self.mng_speaker_id = mng_speaker_id()
        self.cevio = CeVIO()
        self.cleanup_voice_files.start()
        logger.info("MyCog initialized.")

    @tasks.loop(minutes=10)
    async def cleanup_voice_files(self):
        logger.info("Running cleanup_voice_files task.")
        for file in Path('./voice').glob('*.wav'):
            if file.stat().st_mtime < time.time() - 3600:
                file.unlink()
                logger.info(f"Deleted old file: {file}")

    @cleanup_voice_files.before_loop
    async def before_cleanup_voice_files(self):
        logger.info("Waiting for bot to be ready before cleanup task.")
        await self.bot.wait_until_ready()

    async def process_message(self, message):
        logger.debug(f"Processing message: {message.content} from {message.author}")

        if message.author == self.bot.user:
            logger.debug("Message is from bot itself. Ignoring.")
            return
        if message.content.startswith((";", "；", "//")):
            logger.debug("Message starts with ignored prefix. Skipping.")
            return
        if self.channel_id is None or message.channel.id != self.channel_id:
            logger.info(f"Message channel ({message.channel.id}) is not the configured channel ({self.channel_id}). Ignoring.")
            return

        self.content = message.content
        self.user_id = message.author.id
        self.server_id = message.guild.id
        self.message_hash = hash(message)

        voice_id = self.mng_speaker_id.get_voice_id(self.user_id, self.server_id)
        logger.debug(f"Voice ID for user {self.user_id}: {voice_id}")

        try:
            if voice_id is None:
                logger.info("No voice ID found. Using CeVIO with default voice.")
                self.cevio.make_sound_CeVIO(self.content, "IA", f"{self.message_hash}.wav")
            elif voice_id == "IA":
                logger.info("Using CeVIO with IA voice.")
                self.cevio.make_sound_CeVIO(self.content, voice_id, f"{self.message_hash}.wav")
            else:
                logger.info("Using Voicevox for synthesis.")
                self.voicevox_instance.hogehoge(self.content, voice_id, self.message_hash)

            source = discord.FFmpegPCMAudio(f'voice/{self.message_hash}.wav')
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
            else:
                logger.warning("No active voice client.")
        except Exception as e:
            logger.error(f"Error in process_message: {e}")


    @commands.Cog.listener()
    async def on_message(self, message):
        logger.debug(f"Received message: {message.content}")
        asyncio.create_task(self.process_message(message))

    @app_commands.command(name='join', description='Say hello to the world!')
    async def join(self, interaction: discord.Interaction):
        logger.info(f"Received join command from {interaction.user}.")
        self.channel_id = interaction.channel.id
        if interaction.guild.id in self.voice_connections:
            logger.warning("Already connected to a voice channel in this guild.")
            await interaction.response.send_message("既に接続しています。", ephemeral=True)
            return

        if interaction.user.voice and interaction.user.voice.channel:
            voice_channel = interaction.user.voice.channel
            try:
                vc = await voice_channel.connect()
                self.voice_connections[interaction.guild.id] = vc
                logger.info(f"Connected to voice channel: {voice_channel}.")
                await interaction.response.send_message("接続しました。", ephemeral=True)
            except Exception as e:
                logger.error(f"Error connecting to voice channel: {e}")
                await interaction.response.send_message("接続できませんでした。", ephemeral=True)
        else:
            logger.warning("User is not in a voice channel.")
            await interaction.response.send_message("ボイスチャンネルに接続できませんでした。", ephemeral=True)

    @app_commands.command(name='leave', description='ボイスチャンネルから離れる')
    async def leave(self, interaction: discord.Interaction):
        logger.info(f"Received leave command from {interaction.user}.")
        if interaction.guild.id in self.voice_connections:
            vc = self.voice_connections.pop(interaction.guild.id)
            await vc.disconnect()
            logger.info(f"Disconnected from voice channel in guild {interaction.guild.id}.")
            await interaction.response.send_message("切断しました。", ephemeral=True)
        else:
            logger.warning("No active voice connection in this guild.")
            await interaction.response.send_message("ボイスチャンネルに接続していません。", ephemeral=True)

    @tasks.loop(seconds=30)
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