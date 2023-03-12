import requests, os
from dotenv import load_dotenv

load_dotenv()

class MdbLink(object):
  _id: int
  owner_id: InterruptedError
  link: str
  chunk_urls: list[str]
  uuid: str
  file_extension: str

  def __init__(self, data: dict):
    self._id = data.get("_id")
    self.owner_id = data.get("owner_id")
    self.link = data.get("link")
    self.chunk_urls = data.get("chunk_urls")
    self.uuid = data.get("uuid")
    self.file_extension = data.get("file_extension")

  def __repr__(self):
    return f"<MdbLink {self.uuid}>"
  
  def __str__(self):
    return self.__repr__()

class MdbApi(object):
  _url: str = "https://mdb.mzecheru.com/api/24/main"
  headers: dict = { "Authorization": os.getenv("MDB_AUTH") }

  @classmethod
  def url(cls, *args) -> str:
    return cls._url + "".join(args)

  @classmethod    
  def get(cls, url):
    return requests.get(url, headers=cls.headers)
  
  @classmethod
  def get_link_entry_by_uuid(cls, uuid) -> MdbLink or None:
    entries = cls.get(cls.url("/links/?uuid=", uuid)).json()
    return MdbLink(entries[0]) if len(entries) else None

class DiscordApi(object):
  
  @staticmethod
  def get_attachment_by_url(url: str):
    return requests.get(url).iter_content(1024)