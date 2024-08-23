import pickle
import os

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

def load_data(server_id, filename=None):
    if filename is None:
        filename = "server/" + str(server_id) + "/data.pkl"
    
    if os.path.exists(filename):
        with open(filename, 'rb') as file:
            data = pickle.load(file)
        return data
    else:
        return {}

def get_voice_id(now_user_id, server_id, filename=None):
    data = load_data(server_id, filename)
    return data.get(now_user_id, None)

now_user_id = 293747561
server_id = 987654321

save_data(now_user_id, 2, server_id)

voice_id = get_voice_id(now_user_id, server_id)
if voice_id is not None:
    print(f"User ID {now_user_id} has voice ID {voice_id}.")
else:
    print(f"User ID {now_user_id} is not in the data.")