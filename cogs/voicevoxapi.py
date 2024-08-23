import requests
from pathlib import Path


class voicevox:

    def hogehoge(self, text, speaker):
        url = "http://localhost:50021/audio_query"

        text = text[:20]

        params = {"text": text, "speaker": speaker}  # ずんだもん ノーマルスタイル
        timeout = 15
        query_synthesis = requests.post(url, params=params, timeout=timeout)
        # params = {"speaker": 3}

        print(text)

        if(text[0] == ";"):
            return
        response = requests.post(
                    "http://localhost:50021/synthesis",
                    params=params,
                    json=query_synthesis.json(),
                )
        wav = response.content

        path = "voice/sample.wav"
        out = Path(path)
        out.write_bytes(wav)
        print('create file')