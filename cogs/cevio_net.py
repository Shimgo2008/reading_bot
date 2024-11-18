import clr
import re
import os
import settings

class CeVIO:

    def __init__(self):
        dll_path = settings.CEVIO_DLL_PATH
        if not os.path.exists(dll_path):
            raise FileNotFoundError(f"DLL ファイルが見つかりません: {dll_path}")
        clr.AddReference(dll_path)
        from CeVIO.Talk.RemoteService2 import ServiceControl2, Talker2
        self.ServiceControl2 = ServiceControl2
        self.Talker2 = Talker2 

    def make_sound_CeVIO(self, text: str, cast: str):
        print("関数が呼ばれました")
        try:
            # テキストのクリーニング
            def clean_text(text):
                text = re.sub(r'\|\|.+?\|\|', 'ネタバレ', text)
                text = re.sub(r'`[^\n\r\f\v`]+?`|```[\s\S]+?```', 'コード省略', text)
                text = re.sub(r'^(-#\ )?(#{1,3}\ )?;[\s\S]*|//.*?(\n|$)|/\*[\s\S]*?\*/', '\n', text).strip()
                text = text.replace('IA姉', 'いあねえ')
                text = text.replace('ia姉', 'いあねえ')
                text = text.replace("IA", "いあ")
                text = text.replace('`ia', 'いあ')
                return text

            text = clean_text(text)
            text = text[:150]

            # CeVIO AIを起動
            if not self.ServiceControl2.IsHostStarted:
                self.ServiceControl2.StartHost(False)

            # Talker インスタンスを作成
            talker = self.Talker2()
            talker.Cast = cast
            talker.Volume = 100
            talker.ToneScale = 100

            # 出力ディレクトリの確認
            output_dir = ".\\voice"
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "sample.wav")

            # 音声を出力
            state = talker.OutputWaveToFile(text, output_path)
            print(f"音声が保存されました: {output_path}")
            
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            return
