import requests
import os
from pathlib import Path
import re


class voicevox:

    def hogehoge(self, text, speaker, path=None):
        def clean_text(text):
            text = re.sub(r'^(-#\ )?(#{1,3}\ )?;[\s\S]*|//.*?(\n|$)|/\*[\s\S]*?\*/', '\n', text).strip()
            text = re.sub(r'\|\|.+?\|\|', 'ネタバレ', text)
            text = re.sub(r'`[^\n\r\f\v`]+?`|```[\s\S]+?```', 'コード省略', text)
            return text

        url = 'http://localhost:50021/audio_query'

        print(text)

        text = clean_text(text)

        print(text)

        if(text[0] == ';' or text[0:1] == '//'):
            os.rename('voice/sample.wav')
            return

        text = text[:38]
        params = {'text': text, 'speaker': speaker}  # ずんだもん ノーマルスタイル
        timeout = 15
        query_synthesis = requests.post(url, params=params, timeout=timeout)

        response = requests.post(
                    'http://localhost:50021/synthesis',
                    params=params,
                    json=query_synthesis.json(),
                )
        wav = response.content

        if path == None:
            path = 'voice/sample.wav'

        out = Path(path)
        out.write_bytes(wav)
        print('create file')