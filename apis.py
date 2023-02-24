import requests

from drive_dataclasses import User

class DiscordAPI(object):
  pass

class MdbAPI(object):
  mdb_header: dict = { "Authorization": "dac5523e-2be9-4d8a-afe4-492b5bf297fa" }

  @classmethod
  def get_user_by_username(cls, username: str) -> User or None:
    r = requests.get(f"https://mdb.mzecheru.com/api/24/main/users/?username={username}", headers=cls.mdb_header).json()
    return None if len(r) == 0 else r[0]

  @classmethod
  def create_user(cls, username: str, password: str):
    r = requests.post("https://mdb.mzecheru.com/api/24/main/users/", json={ "username": username, "password": password }, headers=cls.mdb_header).json()
    user = User(username=username, password=password).set_id(r.get("_id"))

    # create user's filestructure
    requests.post("https://mdb.mzecheru.com/api/24/main/files/", json={ { "owner_id": user.id, "files": [], "folders": ["/root/"] }}, headers=cls.mdb_header).json()
    
    # check if user has given their token yet
    if r.get("token"): user.set_token(r.get("token"))
    return user