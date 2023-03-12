import os, threading
from flask import Flask, render_template, send_file, request

try:
  os.mkdir("./files/")
except FileExistsError: pass

# delete all existing files
for file in os.listdir("./files/"):
  os.remove(f"./files/{file}")

# keep track of the created files
uuids = {}

from api import DiscordApi, MdbApi, MdbLink
app = Flask(__name__)

# remove file and uuid from uuids list
def delete(path: str):
  # uuid is in the path ./files/{uuid}.ext
  uuid = path.split("/")[-1].split(".")[0]
  os.remove(path)
  del uuids[uuid]

# set a timer to automatically delete a file
def auto_delete(path: str, seconds: int):
  t = threading.Timer(seconds, delete, args=[path])
  t.daemon = True
  t.start()

# returns a path to the made file
def create_file_from(link_obj: MdbLink) -> str:
  urls: list[str] = link_obj.chunk_urls
  file_path: str = f"./files/{link_obj.uuid}.{link_obj.file_extension}"
  
  if uuids.get(link_obj.uuid):
    return file_path
  
  with open(file_path, "wb") as f:
    for url in urls:
      for data_chunk in DiscordApi.get_attachment_by_url(url):
        f.write(data_chunk)

  # automatically delete the file in 20 minutes
  auto_delete(file_path, 20 * 60)
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

if __name__ == "__main__":
  app.run(host="0.0.0.0", port="80", debug=False)