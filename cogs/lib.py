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


class mng_dict:
    def save_dic(self, guild_id: str, original_word: str, word_phonetic: str):
        print(f"guild_id is {guild_id}\noriginal_word is {original_word}\nword_phonetic is {word_phonetic}")
        file_path = f'server/{guild_id}/phonetic_dict.json'

        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = {}
        else:
            data = {}
        data[original_word] = word_phonetic
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return f"「{original_word}」の読みを「{word_phonetic}」として登録しました"

    def remove_dict(self, guild_id: str, original_word: str):
        print(f"guild_id is {guild_id}\noriginal_word to remove is {original_word}")
        # 保存先ファイルパス
        file_path = f'server/{guild_id}/phonetic_dict.json'
        # 既存のデータを読み込む
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                error_msg = "エラー: 辞書ファイルが壊れています。"
                print(error_msg)
                return error_msg
        else:
            error_msg = "エラー: 辞書ファイルが存在しません。"
            print(error_msg)
            return error_msg
        # 指定したキーを削除
        if original_word in data:
            del data[original_word]
            print(f"キー `{original_word}` を辞書から削除しました。")
            # 更新後のデータを保存
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                return f"キー `{original_word}` を削除しました。"
            except Exception as e:
                error_msg = f"エラー: ファイルの保存中に問題が発生しました。詳細: {e}"
                print(error_msg)
                return error_msg
        else:
            error_msg = f"エラー: キー `{original_word}` は辞書に存在しません。"
            print(error_msg)
            return error_msg

    def list_dict(self, guild_id: str):
        with open(f"server/{guild_id}/phonetic_dict.json", "r", encoding='utf-8') as f:
            data = json.load(f)

        data = str(data).replace(',', '\n').replace('{', '').replace('}', '').replace('\'', '')
        return data
