import contextlib
from dataclasses import dataclass
from typing import Optional
import requests

@dataclass
class User(object):
  username: str
  password: str
  token: Optional[str] = None
  id: Optional[int] = None
  server_id: Optional[str] = None

  def set_id(self, id):
    self.id = id
    return self

  def set_token(self, token):
    self.token = token
    requests.put(f"https://mdb.mzecheru.com/api/24/main/users/{self.id}/token", json={ "value": self.token }, headers={ "Authorization": "dac5523e-2be9-4d8a-afe4-492b5bf297fa" })
    return self
  
  def set_server_id(self, server_id):
    self.server_id = server_id
    requests.put(f"https://mdb.mzecheru.com/api/24/main/users/{self.id}/server_id", json={ "value": self.server_id }, headers={ "Authorization": "dac5523e-2be9-4d8a-afe4-492b5bf297fa" })
    return self

class FilePath(object):
  _path: str
  _type: str

  def __init__(self, path, _type):
    self._path = path
    self._type = _type

  def path(self):
    return self._path
  
  def type(self):
    return self._type
  
  def is_folder(self):
    return self._type == "folder"
  
  def parent_path(self) -> str:
    # /parent/folder/ -> /parent/
    with contextlib.suppress(IndexError):
      split = self._path.split("/")
      split[0] = "/" # root
      if self.is_folder():
        # [0] is root, [-1] is empty string because all dir paths end in /
        # [2] is (self) folder
        # [3] is parent folder
        return split[-3] if len(split) >= 3 else split[-2]
      else:
        # [0] is root, [-1] is file
        # [2] is parent folder
        return split[-2] if len(split) >= 2 else split[-1]

  def name(self):
    if self.path() == "/": return "root"
    split = self._path.split("/")
    return split[-2] if split[-1] == "" else split[-1]

  def __str__(self) -> str:
    return f"<{self._type} - {self._path}>"
  
  def __repr__(self) -> str:
    return self.__str__()
  
class DriveFile(object):
  path: str

  def __init__(self, path):
    self._path = path

  def path(self):
    return self._path
  
  def __str__(self) -> str:
    return f"<file - {self._path}>"
  
  def __repr__(self) -> str:
    return self.__str__()

class DriveFolder(DriveFile):
  children: list = []
  _parent_path: any#DriveFolder

  def __init__(self, path, children=None, parent_path=None):
    self._path = path
    self.children = children or []
    self._parent_path = parent_path

  def path(self):
    return self._path
  
  def parent_path(self):
    return self._parent_path
  
  #                                    or DriveFolder
  def add_child(self, child: DriveFile or any):
    self.children.append(child)

  def __str__(self) -> str:
    return f"<folder - {self._path}>"
  
@dataclass
class MdbChannel(object):
  _id: int
  owner_id: int
  channel_id: str
  channel_name: str
  folder_path: str

  @property
  def id(self):
    return self.channel_id
  
@dataclass
class MdbFile(object):
  _id: int
  owner_id: int
  chunk_urls: list[str]
  file_name: str
  folder_path: str
  file_extension: str
  size: str

  @property
  def full_name(self):
    return f"{self.file_name}.{self.file_extension}"
  
  @property
  def path(self):
    return f"{self.folder_path}{self.full_name}"