import requests
import settings
from pathlib import Path
import re


class voicevox:

    def hogehoge(self, text, speaker, filename=None):
        def clean_text(text):
            text = re.sub(r'\|\|.+?\|\|', 'ネタバレ', text)
            text = re.sub(r'`[^\n\r\f\v`]+?`|```[\s\S]+?```', 'コード省略', text)
            text = text.replace('IA姉', 'いあねえ')
            text = text.replace('ia姉', 'いあねえ')
            text = text.replace("IA", "いあ")
            text = text.replace('`ia', 'いあ')
            return text

        url = f'{settings.VOICEVOX_PORT}/audio_query'

        print(text)

        text = clean_text(text)

        print(text)

        # text = text[:240]
        params = {'text': text, 'speaker': speaker}  # ずんだもん ノーマルスタイル
        timeout = 15
        query_synthesis = requests.post(url, params=params, timeout=timeout)
        print(query_synthesis.json())
        response = requests.post(
            f'{settings.VOICEVOX_PORT}/synthesis',
            params=params,
            json=query_synthesis.json(),
        )
        wav = response.content

        if not filename:
            filename = "sword_world_2"

        filename = f'voice/{filename}.wav'

        out = Path(filename)
        out.write_bytes(wav)
        print('create file')
