from io import BufferedReader
import json
import pathlib
import requests

from drive_dataclasses import FilePath, User, MdbChannel, MdbFile

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
  @property
  def token(cls) -> str:
    return cls.header["authorization"]

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
      "topic": path,
      "nsfw": False
    })).json().get('id')

    MdbAPI.create_channel(user_id, _id, name, path)

  @classmethod
  def update_channel_description(cls, channel_id: str, new_description: str):
    return requests.patch(f"{cls.base}/channels/{channel_id}", headers=cls.header, data=json.dumps({ "topic": new_description })).json()

  @classmethod                                                                                                                # returns attachment url (chunk url)
  def upload_file_chunk(cls, chunk: BufferedReader, channel: MdbChannel, user: User, folder: FilePath, name: str, ext: str) -> str:
    # 'chunk' is a chunk of a file saved to its own file
    name = uuid4()
    url = requests.post(f"{cls.base}/channels/{channel.id}/messages", headers={ "authorization": cls.token }, files={ "file" : (f"./{name}", chunk) }).json().get("attachments")[0].get("url")
    chunk.close()
    return url
  
  @classmethod
  def get_attachment_by_url(cls, url: str) -> dict:
    return requests.get(url).iter_content(1024)

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
    requests.post("https://mdb.mzecheru.com/api/24/main/filesystem/", json={ "owner_id": user.id, "files": [], "folders": ["/"] }, headers=cls.mdb_header).json()
    
    # check if user has given their token yet
    if r.get("token"): user.set_token(r.get("token"))
    return user
  
  @classmethod
  def get_user_filesystem_entry_by_userid(cls, user_id: int) -> list:
    r = requests.get(f"https://mdb.mzecheru.com/api/24/main/filesystem/?owner_id={user_id}", headers=cls.mdb_header).json()
    return None if len(r) == 0 else r[0]
  
  @classmethod
  def get_user_folders(cls, user_id: int) -> list[str]:
    return cls.get_user_filesystem_entry_by_userid(user_id).get("folders")
  
  @classmethod
  def get_user_files(cls, user_id: int) -> list[str]:
    return cls.get_user_filesystem_entry_by_userid(user_id).get("files")

  @classmethod
  def update_user_files(cls, entry_id: int, files: list[str]):
    return requests.put(f"https://mdb.mzecheru.com/api/24/main/filesystem/{entry_id}/files", json={ "value": files }, headers=cls.mdb_header).json()
  
  @classmethod
  def update_user_folders(cls, entry_id: int, folders: list[str]):
    return requests.put(f"https://mdb.mzecheru.com/api/24/main/filesystem/{entry_id}/folders", json={ "value": folders }, headers=cls.mdb_header).json()
  
  @classmethod
  def update_filename(cls, entry_id: int, newname: str):
    return requests.put(f"https://mdb.mzecheru.com/api/24/main/files/{entry_id}/file_name", json={ "value": newname }, headers=cls.mdb_header).json()
  
  @classmethod
  def update_file_containing_folder(cls, entry_id: int, new_folder_path: str):
    return requests.put(f"https://mdb.mzecheru.com/api/24/main/files/{entry_id}/folder_path", json={ "value": new_folder_path }, headers=cls.mdb_header).json()
  
  @classmethod
  def get_channel(cls, user_id: int, channel_id: str):
    r = requests.get(f"https://mdb.mzecheru.com/api/24/main/channels/?owner_id={user_id}&channel_id={channel_id}", headers=cls.mdb_header).json()
    return None if len(r) == 0 else r[0]
  
  @classmethod
  def get_channel_by_folder_path(cls, user_id: int, folder_path: str) -> None or MdbChannel:
    r = requests.get(f"https://mdb.mzecheru.com/api/24/main/channels/?owner_id={user_id}&folder_path={folder_path}", headers=cls.mdb_header).json()
    return None if len(r) == 0 else MdbChannel(
      _id=r[0].get("_id"),
      owner_id=r[0].get("owner_id"),
      channel_id=r[0].get("channel_id"),
      channel_name=r[0].get("channel_name"),
      folder_path=r[0].get("folder_path")
    )
  
  @classmethod
  def create_channel(cls, owner_id: int, channel_id: str, channel_name: str, folder_path: str):
    return requests.post("https://mdb.mzecheru.com/api/24/main/channels/", json={ "owner_id": owner_id, "channel_id": channel_id, "channel_name": channel_name, "folder_path": folder_path }, headers=cls.mdb_header).json()
  
  @classmethod
  def update_folder_path(cls, channel_id: str, new_folder_path: str):
    return requests.put(f"https://mdb.mzecheru.com/api/24/main/channels/{channel_id}/folder_path", json={ "value": new_folder_path }, headers=cls.mdb_header).json()
  
  @classmethod
  def upload_file(cls, user_id: int, folder_path: str, name: str, extension: str, size: str, file_chunk_urls: list[str]):
    cls.update_user_files(cls.get_user_filesystem_entry_by_userid(user_id).get("_id"), cls.get_user_files(user_id) + [f"{folder_path}{name}.{extension}"])
    return requests.post("https://mdb.mzecheru.com/api/24/main/files/", json={ "owner_id": user_id, "folder_path": folder_path, "file_name": name, "file_extension": extension, "size": size, "chunk_urls": file_chunk_urls }, headers=cls.mdb_header).json()
  
  @classmethod
  def get_file_metadata(cls, user_id: int, parent_folder: str, file_name: str) -> None or MdbFile:
    name = ".".join(file_name.split(".")[:-1])
    extension = file_name.split(".")[-1]
    
    if not parent_folder.startswith("/"):
      parent_folder = f"/{parent_folder}/"

    r = requests.get(f"https://mdb.mzecheru.com/api/24/main/files/?owner_id={user_id}&folder_path={parent_folder}&file_name={name}&file_extension={extension}", headers=cls.mdb_header).json()
    return None if len(r) == 0 else MdbFile(
      _id=r[0].get("_id"),
      owner_id=r[0].get("owner_id"),
      folder_path=r[0].get("folder_path"),
      file_name=r[0].get("file_name"),
      file_extension=r[0].get("file_extension"),
      size=r[0].get("size"),
      chunk_urls=r[0].get("chunk_urls")
    )

  @classmethod
  def get_files_with_folder_path(cls, user_id: int, parent_folder: str) -> list[MdbFile]:
    r = requests.get(f"https://mdb.mzecheru.com/api/24/main/files/?owner_id={user_id}&folder_path={parent_folder}", headers=cls.mdb_header).json()
    return [MdbFile(
      _id=i.get("_id"),
      owner_id=i.get("owner_id"),
      folder_path=i.get("folder_path"),
      file_name=i.get("file_name"),
      file_extension=i.get("file_extension"),
      size=i.get("size"),
      chunk_urls=i.get("chunk_urls")
    ) for i in r]