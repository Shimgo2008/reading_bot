import pickle
import json
import os

class mng_speaker_id:

    @staticmethod
    def save_data(user_id, voice_id, server_id, filename=None):
        if filename is None:
            filename = "server/" + str(server_id) + "/data.pkl"

        # ディレクトリが存在しない場合は作成する
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        if os.path.exists(filename):
            with open(filename, 'rb') as file:
                data = pickle.load(file)
        else:
            data = {}

        data[user_id] = voice_id

        with open(filename, 'wb') as file:
            pickle.dump(data, file)

    @staticmethod
    def load_data(server_id, filename=None):
        if filename is None:
            filename = "server/" + str(server_id) + "/data.pkl"

        if os.path.exists(filename):
            with open(filename, 'rb') as file:
                data = pickle.load(file)
            return data
        else:
            return {}

    @staticmethod
    def get_voice_id(now_user_id, server_id, filename=None):
        if filename is None:
            filename = "server/" + str(server_id) + "/data.pkl"

        if os.path.exists(filename):
            with open(filename, 'rb') as file:
                data = pickle.load(file)
            return data.get(now_user_id, None)
        else:
            return None

    def save_dic(guild_id:str, original_word:str, word_phonetic:str):
        print(f"guild_id is {guild_id}\noriginal_word is {original_word}\nword_phonetic is {word_phonetic}")
        d_new = {original_word:word_phonetic}
        with open(f'server/{guild_id}/phonetic_dict.j1son', 'w')as f:
            json.dump(d_new, f, indent=0)

    def get_dic(guild_id:str):
        print(guild_id)