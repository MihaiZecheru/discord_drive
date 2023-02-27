import json
import pathlib
import requests

from drive_dataclasses import User

def uuid4() -> str:
  return requests.get("https://www.uuidgenerator.net/api/version4").text

class DiscordAPI(object):
  base: str = "https://discord.com/api/v9"
  header = {
    "authorization": None, # needs to be set
    "Content-Type": "application/json"
  }

  db_server_id: str = None

  @classmethod
  def set_token(cls, token: str):
    cls.header["authorization"] = token
    return token

  @classmethod
  def set_database_server_id(cls, server_id: str):
    cls.db_server_id = server_id
    return server_id

  @classmethod                      # returns server id
  def create_database_server(cls, user_id: int) -> str:
    data_uri = pathlib.Path("./static/discord_drive_data_uri.txt").read_text()

    _id = requests.post(f"{cls.base}/guilds", headers=cls.header, data=json.dumps({
      "name": "DiscordDrive",
      "region": "us-west",
      "icon": data_uri,
      "verification_level": 0,
      "default_message_notifications": 1,
      "explicit_content_filter": 0
    })).json().get('id')
    
    # clear server of channels
    for channel in requests.get(f"{cls.base}/guilds/{_id}/channels", headers=cls.header).json():
      requests.delete(f"{cls.base}/channels/{channel.get('id')}", headers=cls.header)
    
    cls.set_database_server_id(_id)

    # create root channel
    cls.create_channel(user_id, "/")

    # set server id in class
    return cls.db_server_id
  
  @classmethod
  def create_channel(cls, user_id: int, path: str) -> str:
    name = uuid4()
    _id = requests.post(f"{cls.base}/guilds/{cls.db_server_id}/channels", headers=cls.header, data=json.dumps({
      "name": name,
      "type": 0,
      "topic": "folder",
      "nsfw": False
    })).json().get('id')

    MdbAPI.create_channel(user_id, _id, name, path)

class MdbAPI(object):
  mdb_header: dict = { "Authorization": "dac5523e-2be9-4d8a-afe4-492b5bf297fa" }

  @classmethod
  def get_user_by_username(cls, username: str) -> User or None:
    r = requests.get(f"https://mdb.mzecheru.com/api/24/main/users/?username={username}", headers=cls.mdb_header).json()
    return None if len(r) == 0 else r[0]

  @classmethod
  def create_user(cls, username: str, password: str):
    # create user
    r = requests.post("https://mdb.mzecheru.com/api/24/main/users/", json={ "username": username, "password": password }, headers=cls.mdb_header).json()
    user = User(username=username, password=password).set_id(r.get("_id"))

    # create user's filestructure
    requests.post("https://mdb.mzecheru.com/api/24/main/files/", json={ "owner_id": user.id, "files": [], "folders": ["/"] }, headers=cls.mdb_header).json()
    
    # check if user has given their token yet
    if r.get("token"): user.set_token(r.get("token"))
    return user
  
  @classmethod
  def get_user_filesystem_entry_by_id(cls, user_id: int) -> list:
    r = requests.get(f"https://mdb.mzecheru.com/api/24/main/files/?owner_id={user_id}", headers=cls.mdb_header).json()
    return None if len(r) == 0 else r[0]
  
  @classmethod
  def get_user_folders(cls, user_id: int) -> list[str]:
    return cls.get_user_filesystem_entry_by_id(user_id).get("folders")
  
  @classmethod
  def get_user_files(cls, user_id: int) -> list[str]:
    return cls.get_user_filesystem_entry_by_id(user_id).get("files")

  @classmethod
  def update_user_files(cls, entry_id: int, files: list[str]):
    return requests.put(f"https://mdb.mzecheru.com/api/24/main/files/{entry_id}/files", json={ "value": files }, headers=cls.mdb_header).json()
  
  @classmethod
  def update_user_folders(cls, entry_id: int, folders: list[str]):
    return requests.put(f"https://mdb.mzecheru.com/api/24/main/files/{entry_id}/folders", json={ "value": folders }, headers=cls.mdb_header).json()
  
  @classmethod
  def get_channel(cls, channel_id: str):
    r = requests.get(f"https://mdb.mzecheru.com/api/24/main/channels/?channel_id={channel_id}", headers=cls.mdb_header).json()
    return None if len(r) == 0 else r[0]
  
  @classmethod
  def get_channel_by_folder_path(cls, folder_path: str):
    r = requests.get(f"https://mdb.mzecheru.com/api/24/main/channels/?folder_path={folder_path}", headers=cls.mdb_header).json()
    return None if len(r) == 0 else r[0]
  
  @classmethod
  def create_channel(cls, owner_id: int, channel_id: str, channel_name: str, folder_path: str):
    return requests.post("https://mdb.mzecheru.com/api/24/main/channels/", json={ "owner_id": owner_id, "channel_id": channel_id, "channel_name": channel_name, "folder_path": folder_path }, headers=cls.mdb_header).json()
  
  @classmethod
  def update_folder_path(cls, channel_id: str, new_folder_path: str):
    return requests.put(f"https://mdb.mzecheru.com/api/24/main/channels/{channel_id}/folder_path", json={ "value": new_folder_path }, headers=cls.mdb_header).json()