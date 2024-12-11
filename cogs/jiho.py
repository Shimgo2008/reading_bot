import datetime
import discord
import asyncio
import logging

logger = logging.getLogger(__name__)  # ファイル名をロガー名として使用


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
        self.jiho = False

        while True:
            now = datetime.datetime.now()
            logger.info(now)

            hour = now.hour
            minute = now.minute

            match (hour, minute):
                case (0, 0):
                    if not self.jiho:
                        logger.info("00:00:00 detected. Playing audio.")
                        await self.play_voice("all", "protect_voice_data/niconico_ziho_0h.wav")
                        self.jiho = True
                        await asyncio.sleep(90)  # 90秒待機後フラグリセット

                case (1, 0):
                    if not self.jiho:
                        logger.info("01:00:00 detected. Playing audio.")
                        await self.play_voice("all", "protect_voice_data/niconico_ziho_1h.wav")
                        self.jiho = True
                        await asyncio.sleep(90)

                case (2, 0):
                    if not self.jiho:
                        logger.info("02:00:00 detected. Playing audio.")
                        await self.play_voice("all", "protect_voice_data/niconico_ziho_2h.wav")
                        self.jiho = True
                        await asyncio.sleep(90)

            # フラグをリセット
            if minute != 0:
                self.jiho = False

            if hour not in [0, 1, 23]:
                await asyncio.sleep(1200)
            elif minute > 54:
                print("30秒待機します")
                await asyncio.sleep(15)
            elif minute > 30:
                print("5分待機します")
                await asyncio.sleep(300)
            else:
                print("10分待機します")
                await asyncio.sleep(600)
