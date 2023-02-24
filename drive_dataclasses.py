from dataclasses import dataclass
from typing import Optional
import requests

@dataclass
class User(object):
  username: str
  password: str
  token: Optional[str] = None
  id: Optional[int] = None

  def set_id(self, id):
    self.id = id
    return self

  def set_token(self, token):
    self.token = token
    requests.put(f"https://mdb.mzecheru.com/api/24/main/users/{self.id}/token", json={ "value": self.token }, headers={ "Authorization": "dac5523e-2be9-4d8a-afe4-492b5bf297fa" }).json()
    return self

class FilePath(object):
  _path: str

  def __init__(self, path):
    self._path = path

  def path(self):
    return self._path
  
class DriveFolder(FilePath):
  children: list # list of DriveFolder/DriveFile

  def __init__(self, path, children=[]):
    self._path = path
    self.children = children

class DriveFile(FilePath):
  pass