import datetime
import discord
import asyncio
import logging

logger = logging.getLogger("jiho")

class jiho:
    def __init__(self, voice_connections):
        """
        初期化
        :param voice_connections: 現在のボイスチャンネル接続を管理する辞書
        """
        self.voice_connections = voice_connections

    async def play_voice(self, guild_id, filepath):
        """
        音声を再生する
        :param guild_id: サーバーID
        :param filepath: 再生する音声ファイルのパス
        """
        try:
            # すべての接続されているボイスチャンネルで音声を再生
            for guild_id, vc in self.voice_connections.items():
                if vc and vc.is_connected():
                    source = discord.FFmpegPCMAudio(filepath)
                    if not vc.is_playing():
                        vc.play(source)
                        logger.info(f"Playing audio in guild {guild_id}.")
                    else:
                        logger.warning(f"Audio is already playing in guild {guild_id}.")
                else:
                    logger.warning(f"No active voice client in guild {guild_id}.")
        except Exception as e:
            logger.error(f"Error playing voice in guild {guild_id}: {e}")

    async def jiho_task(self):
        """
        時報タスク
        """
        self.jiho = False  # jiho フラグを初期化

        while True:
            now = datetime.datetime.now()
            logger.info(now)

            hour = now.hour
            minute = now.minute

            if hour == 0 and minute == 0 and not self.jiho:  # 00:00:00 とフラグが False の時
                logger.info("00:00:00 detected. Playing audio.")
                await self.play_voice("all", "protect_voice_data/niconico douga onsei.wav")
                await asyncio.sleep(90)  # 90秒待機後フラグリセット

            if hour != 23:
                await asyncio.sleep(1200)
            elif minute > 55:
                await asyncio.sleep(30)
            elif minute > 30:
                await asyncio.sleep(300)
            else:
                await asyncio.sleep(600)