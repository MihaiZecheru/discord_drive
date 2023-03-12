import os
from flask import Flask, render_template, send_file, request

try:
  os.mkdir("./files/")
except FileExistsError: pass

try:
  with open("./uuids.txt", "r") as f: pass
except FileNotFoundError:
  with open("./uuids.txt", "w") as f: pass

# keep track of the created files
uuids = {}

# populate uuids list
try:
  with open("./uuids.txt", "r") as f:
    for line in f:
      uuid, path = line.strip().split(";")
      uuids[uuid] = path
except ValueError: pass # uuids = {}

from api import DiscordApi, MdbApi, MdbLink
app = Flask(__name__)

# returns a path to the made file
def create_file_from(link_obj: MdbLink) -> str:
  urls: list[str] = link_obj.chunk_urls
  file_path: str = f"./files/{link_obj.uuid}.{link_obj.file_extension}"
  
  if uuids.get(link_obj.uuid):
    return file_path
  
  with open("./uuids.txt", "a") as f:
    uuids[link_obj.uuid] = file_path
    f.write(f"{link_obj.uuid};{file_path}\n")

  with open(file_path, "wb") as f:
    for url in urls:
      for data_chunk in DiscordApi.get_attachment_by_url(url):
        f.write(data_chunk)

  return file_path

@app.route("/")
def root():
  return render_template("index.html")

@app.route("/<uuid>")
def get_file(uuid):
  # the first time this request is executed, the spinner screen will be shown
  # on the second request, the file is created and sent to the user

  if not request.args.get("u"):
    # send the file if it exists, otherwise send the spinner screen    
    if path := uuids.get(uuid):
      return send_file(path)

    return render_template("spinner.html", uuid=uuid)
  
  # the below code will execute the second time this request is made, indicated by the "u" query param
  # this is all done to allow the spinner screen to show while the file is being created from the chunk_urls
  
  link_obj: MdbLink or None = MdbApi.get_link_entry_by_uuid(uuid)
  
  if not link_obj:
    return f"<p>File with ID \"{uuid}\" does not exists</p>"
  
  file_path: str = create_file_from(link_obj)
  return send_file(file_path)

app.run(debug=True)