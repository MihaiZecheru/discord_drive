import contextlib
import math
import os
import re
from PIL import ImageTk, Image
import customtkinter as ctk
import tkinter.ttk as ttk
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import imghdr, mimetypes
from tkVideoPlayer import TkinterVideo
import pyperclip
from drive_dataclasses import DriveFolder, FilePath, MdbChannel, MdbFile, User
from apis import DiscordAPI, MdbAPI, uuid4

# 25 MB in bytes, discord's max file size
FILE_SIZE_LIMIT = 25000000
FIFTY_GB = 50000000000

def convert_bytes(size):
  """ Convert bytes to KB, MB, GB, or TB """
  for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
      if size < 1024.0:
          return "%3.1f %s" % (size, x)
      size /= 1024.0

class AppPages(ctk.CTk):
  def __init__(self):
    super().__init__()
    self.geometry("500x500")
    self.iconbitmap("./static/icon.ico")
    self.title("DiscordDrive")
    self.resizable(False, False)

  def set_fullscreen(self):
    self.attributes("-fullscreen", True)

  def show_login(self):
    try: self.register_frame.destroy()
    except: pass

    self.login_frame = ctk.CTkFrame(master=self)
    self.login_frame.pack(padx=20, pady=60, fill="both", expand=True)

    ctk.CTkLabel(master=self.login_frame, text="Login To DiscordDrive", font=("Roboto", 27)).pack(pady=5)
    
    # entries frame
    self.entries_frame = ctk.CTkFrame(master=self.login_frame, fg_color=None)
    self.entries_frame.place(relx=.5, rely=.35, anchor=ctk.CENTER)

    # username frame
    self.username_frame = ctk.CTkFrame(master=self.entries_frame)
    self.username_frame.pack(pady=10, fill="both", expand=True, padx=5)
    
    # username entry label
    ctk.CTkLabel(master=self.username_frame, text="Username", font=("Roboto", 15)).pack(side="left", padx=5)
    self.username_box = ctk.CTkEntry(master=self.username_frame)
    self.username_box.pack(side="right", padx=5)

    # password frame
    self.password_frame = ctk.CTkFrame(master=self.entries_frame)
    self.password_frame.pack(pady=10, fill="both", expand=True, padx=5)

    # password entry label
    ctk.CTkLabel(master=self.password_frame, text="Password", font=("Roboto", 15)).pack(side="left", padx=5)
    self.password_box = ctk.CTkEntry(master=self.password_frame, show="*")
    self.password_box.pack(side="right", padx=5)

    # buttons frame
    self.buttons_frame = ctk.CTkFrame(master=self.login_frame)
    self.buttons_frame.place(relx=.5, rely=.6, anchor=ctk.CENTER)

    # login button
    self.login_button = ctk.CTkButton(master=self.buttons_frame, text="Login", font=("Roboto", 15), command=self.login)
    self.login_button.pack(padx=5, pady=5, expand=False)

    # 'go to register' button
    self.go_to_register_button = ctk.CTkButton(master=self.buttons_frame, text="Register", font=("Roboto", 15), command=self.show_register)
    self.go_to_register_button.pack(padx=5, pady=5, expand=False)

    # events
    self.username_box.bind("<Return>", lambda event: self.password_box.focus())
    self.username_box.bind("<Control-BackSpace>", lambda event: self.username_box.delete(0, "end"))
    self.password_box.bind("<Return>", lambda event: self.login())
    self.password_box.bind("<Control-BackSpace>", lambda event: self.password_box.delete(0, "end"))

  def show_register(self):
    self.login_frame.destroy()

    self.register_frame = ctk.CTkFrame(master=self)
    self.register_frame.pack(padx=20, pady=60, fill="both", expand=True)

    ctk.CTkLabel(master=self.register_frame, text="Register To DiscordDrive", font=("Roboto", 27)).pack(pady=5)
    
    # entries frame
    self.entries_frame = ctk.CTkFrame(master=self.register_frame, fg_color=None)
    self.entries_frame.place(relx=.5, rely=.35, anchor=ctk.CENTER)

    # username frame
    self.username_frame = ctk.CTkFrame(master=self.entries_frame)
    self.username_frame.pack(pady=10, fill="both", expand=True, padx=5)
    
    # username entry label
    ctk.CTkLabel(master=self.username_frame, text="Username", font=("Roboto", 15)).pack(side="left", padx=5)
    self.username_box = ctk.CTkEntry(master=self.username_frame)
    self.username_box.pack(side="right", padx=5)

    # password frame
    self.password_frame = ctk.CTkFrame(master=self.entries_frame)
    self.password_frame.pack(pady=10, fill="both", expand=True, padx=5)

    # password entry label
    ctk.CTkLabel(master=self.password_frame, text="Password", font=("Roboto", 15)).pack(side="left", padx=5)
    self.password_box = ctk.CTkEntry(master=self.password_frame, show="*")
    self.password_box.pack(side="right", padx=5)

    # buttons frame
    self.buttons_frame = ctk.CTkFrame(master=self.register_frame)
    self.buttons_frame.place(relx=.5, rely=.6, anchor=ctk.CENTER)

    # login button
    self.go_to_login_button = ctk.CTkButton(master=self.buttons_frame, text="Login", font=("Roboto", 15), command=self.show_login)
    self.go_to_login_button.pack(padx=5, pady=5, expand=False)

    # 'go to register' button
    self.register_button = ctk.CTkButton(master=self.buttons_frame, text="Register", font=("Roboto", 15), command=self.register)
    self.register_button.pack(padx=5, pady=5, expand=False)

    # events
    self.username_box.bind("<Return>", lambda event: self.password_box.focus())
    self.username_box.bind("<Control-BackSpace>", lambda event: self.username_box.delete(0, "end"))
    self.password_box.bind("<Return>", lambda event: self.register())
    self.username_box.bind("<Control-BackSpace>", lambda event: self.password_box.delete(0, "end"))

  def show_main(self):
    self.set_fullscreen()

    self.style = ttk.Style(self)
    self.style.theme_use("clam")
    self.style.configure("Treeview", background="#212121", fieldbackground="#212121", foreground="white", font=("Roboto", 13), borderwidth=0)

    try: self.login_frame.destroy()
    except: pass
    try: self.register_frame.destroy()
    except: pass

    # match color of 'self'
    self.configure(fg_color="#212121")

    # header
    self.header_frame = ctk.CTkFrame(master=self, bg_color="#212121")
    self.header_frame.pack(fill="both", pady=(0, 10))
    ctk.CTkLabel(master=self.header_frame, text="DiscordDrive", font=("Roboto", 35), fg_color=None).pack(pady=5)

    # body
    self.main_frame = ctk.CTkFrame(master=self)
    self.main_frame.pack(side=ctk.TOP, anchor=ctk.NW, fill="both", expand=True)

    # this page will contain a header and a body
    # within the body there will be two frames separated by a vertical divider in the center
    # the left frame will contain the file tree
    # right clicking an item in this file tree frame will reveal a contextmenu that contains buttons to create a new folder, delete the selected file/folder, edit a file's name, and to download the file
    # the right frame will contain a box with the ability to upload a new file via drag and drop of the file explorer

    # file tree frame
    self.file_tree_frame = ctk.CTkFrame(master=self.main_frame, bg_color="#212121", height=100)
    # stick to left side of grid
    self.file_tree_frame.pack(side="left", fill="both", expand=True)

    # file tree frame header
    self.file_tree_header_frame = ctk.CTkFrame(master=self.file_tree_frame, bg_color="#212121")
    self.file_tree_header_frame.pack(fill="both", expand=False)
    ctk.CTkLabel(master=self.file_tree_header_frame, text="File System", font=("Roboto", 27), fg_color=None).pack(pady=5)

    # vertical separator
    self.separator = ttk.Separator(master=self.main_frame, orient="vertical")
    self.separator.pack(side="left", fill="y", expand=False)

    # view / upload frame
    self.view_and_upload_frame = ctk.CTkFrame(master=self.main_frame, bg_color="#212121")
    # stick to right side of grid
    self.view_and_upload_frame.pack(side="right", fill="both", expand=True)

    # view / upload frame header
    self.view_and_upload_header_frame = ctk.CTkFrame(master=self.view_and_upload_frame, bg_color="#212121")
    self.view_and_upload_header_frame.pack(fill="both", expand=False)
    ctk.CTkLabel(master=self.view_and_upload_header_frame, text="View / Upload", font=("Roboto", 27), fg_color=None).pack(pady=5)

    # file tree
    self.file_tree = ttk.Treeview(master=self.file_tree_frame, selectmode="browse", show="tree")
    self.file_tree.pack(fill="both", expand=True)

    ### populate file tree
    # root folder
    tree_root = self.file_tree.insert("", "end", text="root", open=True, tags=("folder", "/"))
    self.filetree_iids["/"] = tree_root

    user_entry = MdbAPI.get_user_filesystem_entry_by_userid(self.user.id)
    folders = user_entry.get("folders")
    folders.remove("/")
    folders: list[FilePath] = list(map(lambda folder: FilePath(folder, "folder"), folders))

    filesystem = {
      "root": {
        "folder": DriveFolder("/", [], "/"),
        "treelist_item": tree_root
      }
    }

    def find_folder(name: str, parent_name: str) -> dict:
      matching = []
      for folder_name in filesystem:
        if folder_name == name:
          matching.append(filesystem[folder_name])

      if len(matching) == 1: return matching[0]
      # else
      for folder in matching:
        if FilePath(f"/{folder.parent_path()}/", "folder").name() == parent_name: return folder

    while len(folders):
      for folder in folders:
        parent = FilePath(folder.parent_path(), "folder") #            get parent's parent
        parent_treelist_item = find_folder(parent.name(), FilePath(f"/{parent.parent_path()}/", "folder").name()).get("treelist_item")

        filesystem[folder.name()] = {
          "folder": DriveFolder(folder, [], folder.parent_path()),
          "treelist_item": self.file_tree.insert(parent_treelist_item, "end", text=folder.name(), open=True, tags=("folder", folder.path()))
        }

        self.filetree_iids[folder.path()] = filesystem[folder.name()].get("treelist_item")
        folders.remove(folder)

    files = user_entry.get("files")
    files: list[FilePath] = list(map(lambda file: FilePath(file, "file"), files))

    while len(files):
      for file in files:
        containing_dir = FilePath(file.parent_path(), "folder")
        containing_dir_treelist_item = find_folder(containing_dir.name(), FilePath(f"/{containing_dir.parent_path()}/", "folder").name()).get("treelist_item")
        self.filetree_iids[file.path()] = self.file_tree.insert(containing_dir_treelist_item, "end", text=file.name(), open=True, tags=("file", file.path()))
        files.remove(file)

    # file tree contextmenu
    self.file_tree_contextmenu = tk.Menu(master=self.file_tree_frame, tearoff=False)
    self.file_tree_contextmenu.add_command(label="View", command=lambda: self.view_file(self.get_FilePath_obj()))
    self.file_tree_contextmenu.add_command(label="Download", command=lambda: self.download_file(self.get_FilePath_obj()))
    self.file_tree_contextmenu.add_command(label="Rename", command=lambda: self.rename_file(self.get_FilePath_obj(), "File"))
    self.file_tree_contextmenu.add_command(label="Delete", command=lambda: self.delete_file(self.get_FilePath_obj()))
    self.file_tree_contextmenu.add_command(label="Copy Link", command=lambda: self.create_link(self.get_FilePath_obj()))
    self.file_tree_contextmenu.add_command(label="New Folder", command=lambda: self.new_folder(self.get_FilePath_obj()))

    # file tree contextmenu for folders only
    self.file_tree_folder_contextmenu = tk.Menu(master=self.file_tree_frame, tearoff=False)
    self.file_tree_folder_contextmenu.add_command(label="Rename", command=lambda: self.rename_file(self.get_FilePath_obj(), "Folder"))
    self.file_tree_folder_contextmenu.add_command(label="Delete", command=lambda: self.delete_file(self.get_FilePath_obj()))
    self.file_tree_folder_contextmenu.add_command(label="New Folder", command=lambda: self.new_folder(self.get_FilePath_obj()))

    # bind right click to file tree contextmenu
    self.file_tree.bind("<Button-3>", self.open_file_tree_contextmenu)

    def set_selected_dir(event):
      with contextlib.suppress(IndexError):
        # get the item that was right clicked
        item = self.file_tree.identify("item", event.x, event.y)

        # select the item
        self.file_tree.selection_set(item)

        # only for folders
        if self.selection_has_tag("folder"):
          self.selected_dir = self.get_FilePath_obj()

    self.file_tree.bind("<Button-1>", set_selected_dir)

    ### view_and_upload_header_frame

    # upload frame
    self.upload_frame = ctk.CTkFrame(master=self.view_and_upload_frame, bg_color="#212121")
    self.upload_frame.pack(fill="x", expand=True, anchor=tk.N, side="top")

    # upload buttons frame
    self.upload_buttons_frame = ctk.CTkFrame(master=self.upload_frame, bg_color="#212121")
    self.upload_buttons_frame.pack(fill="x", expand=True, anchor=tk.N, side="top")

    # select file to upload through file explorer
    self.select_file_to_upload_button = ctk.CTkButton(master=self.upload_buttons_frame, text="Select Files", command=lambda: self.preview_files_before_uploading(filedialog.askopenfilenames()))
    self.select_file_to_upload_button.pack(padx=5, side="left", fill="x", expand=True)

    # upload files
    self.upload_file_button = ctk.CTkButton(master=self.upload_buttons_frame, text="Upload Files", command=lambda: self.upload_files(self.get_explorer_selected_files()))
    self.upload_file_button.pack(padx=5, side="right", fill="x", expand=True)

  def show_token_and_server_id_entry_screen(self):
    # header
    self.header_frame = ctk.CTkFrame(master=self, bg_color="#2f3136")
    self.header_frame.pack(fill="both", expand=True)

    # header title
    ctk.CTkLabel(master=self.header_frame, text="DiscordDrive", font=("Roboto", 27), fg_color=None).pack()

    # enter server_id frame
    self.enter_server_id_frame = ctk.CTkFrame(master=self, bg_color="#2f3136")
    self.enter_server_id_frame.pack(fill="both", expand=True)

    # enter server_id label
    ctk.CTkLabel(master=self.enter_server_id_frame, text="Enter Database Server ID", font=("Roboto", 15), fg_color=None).pack(pady=(0, 5))

    # enter server_id entry
    self.server_id_box = ctk.CTkEntry(master=self.enter_server_id_frame)
    self.server_id_box.pack(pady=5)

    # enter token frame
    self.enter_token_frame = ctk.CTkFrame(master=self, bg_color="#2f3136")
    self.enter_token_frame.pack(fill="both", expand=True)

    # enter token label
    ctk.CTkLabel(master=self.enter_token_frame, text="Enter Token", font=("Roboto", 15), fg_color=None).pack(pady=5)

    # enter token entry
    self.token_box = ctk.CTkEntry(master=self.enter_token_frame)
    self.token_box.pack(pady=5)

    # btns frame
    self.btns_frame = ctk.CTkFrame(master=self.enter_token_frame, bg_color="#2f3136")
    self.btns_frame.pack(pady=5)

    # btns
    self.register_user_button = ctk.CTkButton(master=self.btns_frame, text="Register", font=("Roboto", 15), command=self.create_user)
    self.register_user_button.pack()
    self.token_help_button = ctk.CTkButton(master=self.btns_frame, text="Token Help", font=("Roboto", 15), command=self.show_token_help)
    self.token_help_button.pack(pady=(5, 0))
    self.server_id_help_button = ctk.CTkButton(master=self.btns_frame, text="Server ID Help", font=("Roboto", 15), command=self.show_server_id_help)
    self.server_id_help_button.pack(pady=(5, 0))

    # events
    self.token_box.bind("<Return>", lambda event: self.create_user())
    self.token_box.bind("<Control-BackSpace>", lambda event: self.token_box.delete(0, "end"))
    self.server_id_box.bind("<Return>", lambda event: self.token_box.focus)
    self.server_id_box.bind("<Control-BackSpace>", lambda event: self.server_id_box.delete(0, "end"))

  def show_token_help(self):
    # help window
    hw = ctk.CTkToplevel(self)
    hw.title("Finding Discord Token")
    hw.geometry("1150x550")
    hw.iconbitmap("./static/icon.ico")

    info = """As a Discord User, your token is a unique identifier used to authorize your requests when interacting with Discord, either through the client or the API.

    Your token is needed in order to interact with the Discord API to retrieve/upload files later on.

    Here are the steps to finding your token:

      1. Open discord in your browser

      2. Press ctrl+shift+i (hold down ctrl & shift then press i) to open the "developer tools"

      3. In the top of this menu there should be a menu titled "Network". Press it if you see it
          - If you don't see it, click on the double-arrow at the top and select the "Network" menu from the dropdown

      4. In this Network menu you can see all the requests that are sent to the API from the client as you interact with Discord. Find the "Filter" searchbox in the top-left

      5. In this filter box, type "/api" (without the quotes) to filter the requests you're seeing to those from the Discord API

      6. Press ctrl+r (hold down ctrl then press r) to refresh the page or do so by pressing the refresh button manually

      7. Wait for the requests to begin appearing in the log you're viewing.

      8. Click on any of the requests there except for any that end with ".json"

      9. Click on the "headers" tab at the top of the request you're looking at. Note that it may have been selected by default

      10. Scroll until you see the word "authorization". Your token is the value to the right of this word. Copy this value and paste it into DiscordDrive."""

    ctk.CTkLabel(master=hw, text=info, font=("Roboto", 15)).pack()
    hw.mainloop()

  def show_server_id_help(self):
    # help window
    hw = ctk.CTkToplevel(self)
    hw.title("Finding Discord Token")
    hw.geometry("1000x375")
    hw.iconbitmap("./static/icon.ico")

    info = """Do not use any random server for this application!

    You must:
    
    1. Make a brand new server. Don't worry about any of the customizations or the name, the program will change the server's settings automatically

    2. Copy the ID

    To copy the server's ID:

    1. Enable developer mode, go to your user settings --> advanced --> toggle the checkbox at the top

    2. Right click on the icon of the server you've just made

    3. Click on "copy server id" at the bottom of

    4. Paste it into DiscordDrive"""

    ctk.CTkLabel(master=hw, text=info, font=("Roboto", 15)).pack()
    hw.mainloop()

  def invalid_login(self):
    self.username_box.configure(state="normal")
    self.password_box.configure(state="normal")
    self.login_button.configure(state="normal")

    self.username_box.delete(0, "end")
    self.password_box.delete(0, "end")

    messagebox.showinfo("Login Failed", "Invalid username and/or password")
    self.username_box.focus()

  def invalid_register(self):
    self.username_box.configure(state="normal")
    self.password_box.configure(state="normal")
    self.register_button.configure(state="normal")

    self.username_box.delete(0, "end")
    self.password_box.delete(0, "end")
    
    messagebox.showinfo("Username Taken", "This username is unavailable")
    self.username_box.focus()

class Application(AppPages):
  user: User or None = None
  selected_dir: FilePath or None = None
  filetree_iids: dict = { }

  def __init__(self):
    super().__init__()
    self.show_login()
    self.username_box.focus()
    self.explorer_selected_files = []

  def login(self) -> bool or None:
    username = self.username_box.get()
    password = self.password_box.get()

    if not username or not password: return None

    self.username_box.configure(state="disabled")
    self.password_box.configure(state="disabled")
    self.login_button.configure(state="disabled")
    
    # get password of user with given username
    user = MdbAPI.get_user_by_username(username)

    # invalid username
    if user is None:
      return self.invalid_login()

    actual_password = user.get("password")

    # check if password is correct
    if password == actual_password:
      self.login_frame.destroy()
      self.user = User(user.get("username"), user.get("password")).set_id(user.get("_id"))

      if user.get("token") is None:
        return self.show_token_and_server_id_entry_screen()
      
      self.user.token = user.get("token")
      DiscordAPI.set_token(self.user.token)

      if user.get("server_id") is None:
        self.user.set_server_id(DiscordAPI.create_database_server(self.user.id))
      else:
        self.user.set_server_id(user.get("server_id"))

      DiscordAPI.set_database_server_id(self.user.server_id)
      self.show_main()
    else:
      self.invalid_login()

  def register(self):  # sourcery skip: use-named-expression
    username = self.username_box.get()
    password = self.password_box.get()

    if not username or not password: return None

    self.username_box.configure(state="disabled")
    self.password_box.configure(state="disabled")
    self.register_button.configure(state="disabled")

    # check if username is taken
    user = MdbAPI.get_user_by_username(username)

    if user is not None:
      return self.invalid_register()

    self.user = MdbAPI.create_user(username, password)
    self.register_frame.destroy()
    self.show_token_and_server_id_entry_screen()

  def create_user(self):
    token = self.token_box.get().strip()
    if not token: return None

    server_id = self.server_id_box.get().strip()
    if not server_id: return none

    self.token_box.configure(state="disabled")
    self.register_user_button.configure(state="disabled")

    self.user.set_token(token)
    DiscordAPI.set_token(token)

    self.user.set_server_id(server_id)
    DiscordAPI.set_database_server_id(server_id)
    DiscordAPI.customize_server(self.user.id)

    for widget in self.winfo_children():
      widget.destroy()
    
    self.show_main()

  def get_selected(self):
    return self.file_tree.selection()[0]

  def get_FilePath_obj(self) -> FilePath:
    return FilePath(
      # path
      self.file_tree.item(self.get_selected(), "tags")[1],
      # datatype
      self.file_tree.item(self.get_selected(), "tags")[0]
    )

  def selection_has_tag(self, tag):
    return tag in self.file_tree.item(self.file_tree.selection()[0], "tags")

  def upload_files(self, files: list):
    if not files: return

    if self.selected_dir is None:
      return messagebox.showerror("Upload Files", "No folder has been selected as the destination for the file upload. Right click on a folder to select it.")

    if not messagebox.askokcancel("Upload Files", f"Files will be uploaded to {self.selected_dir.path()}"): return
    for file in files:
      self.upload_file(file)

    try: self.preview_frame.destroy()
    except: pass

    self.selected_dir = None

  def upload_file(self, file):
    name = ".".join(file.split("/")[-1].split(".")[:-1])
    ext = file.split("/")[-1].split(".")[-1]

    if re.match(r"^[a-zA-Z0-9_\-]+$", name) is None:
      rn_win = ctk.CTkToplevel(self)
      rn_win.title("Rename File")
      rn_win.geometry("250x200")
      rn_win.iconbitmap("./static/icon.ico")
      rn_win.attributes("-topmost", True)
      rn_win.resizable(False, False)

      ctk.CTkLabel(rn_win, text="File name should be alphanumeric").pack()
      ctk.CTkLabel(rn_win, text="It may contain underscores & dashes").pack()
      ctk.CTkLabel(rn_win, text="Rename File").pack(pady=(10, 0))
      name_entry = ctk.CTkEntry(rn_win)
      name_entry.pack(pady=(0, 10))

      name_entry.insert(0, name)

      old_name_frame = ctk.CTkFrame(rn_win)
      old_name_frame.pack(side=tk.BOTTOM, pady=(0, 10), ipadx=5)

      ctk.CTkLabel(old_name_frame, text="Old Name:").pack()
      ctk.CTkLabel(old_name_frame, text=name).pack()

      def enter_event(file):
        name = name_entry.get()
        if re.match(r"^[a-zA-Z0-9_\-]+$", name) is None:
          messagebox.showerror("Invalid File Name", "The file name should be alphanumeric. It may contain underscores and dashes.")
        else:
          rn_win.destroy()
          os.rename(file, f"{os.path.dirname(file)}/{name}.{ext}")
          file = f"{os.path.dirname(file)}/{name}.{ext}"
          self._upload_file(file, name, ext)

      name_entry.bind("<Return>", lambda e: enter_event(file))
    else:
      file = f"{os.path.dirname(file)}/{name}.{ext}"
      self._upload_file(file, name, ext)

  def _upload_file(self, absolute_filepath, name, ext):
    ### error handling is done, ready to upload

    # get file size
    size = os.path.getsize(absolute_filepath)

    if size > FIFTY_GB:
      return messagebox.showerror("File Too Large", "Maximum file size is 50 GB")

    # how many chunks will the file be split into
    chunks = math.ceil(size / FILE_SIZE_LIMIT)

    with open(absolute_filepath, "rb") as f:
      file = f.read()

    with contextlib.suppress(FileExistsError):
      os.mkdir("./tmp/")

    for i in range(chunks):
      chunk = file[i * FILE_SIZE_LIMIT: (i + 1) * FILE_SIZE_LIMIT]
      with open(f"./tmp/{i}", "wb") as f:
        f.write(chunk)
    
    # get discord channel to upload in
    channel: MdbChannel = MdbAPI.get_channel_by_folder_path(self.user.id, self.selected_dir.path())

    # note: all files are closed inside of the upload_file_chunk function
    file_chunk_urls = [ DiscordAPI.upload_file_chunk(open(f"./tmp/{i}", "rb"), channel, self.user, self.selected_dir, name, ext) for i in range(chunks) ]

    # upload to file tracker in MDB
    MdbAPI.upload_file(self.user.id, self.selected_dir.path(), name, ext, convert_bytes(os.path.getsize(absolute_filepath)).replace(" ", ""), file_chunk_urls)

    # delete all files in tmp dir
    for f in os.listdir('./tmp'):
      os.remove(os.path.join('./tmp', f))

    # add file to file tree
    path = f"{self.selected_dir.path()}{name}.{ext}"
    self.filetree_iids[path] = self.file_tree.insert(self.filetree_iids.get(self.selected_dir.path()), "end", text=f"{name}.{ext}", tags=("file", path))

  def create_link(self, filepath: FilePath):
    # get file metadata
    mdbfile: MdbFile = MdbAPI.get_file_metadata(self.user.id, filepath.parent_path(), filepath.name())

    # create url with random uuid
    uuid = uuid4()
    link = f"http://discord-drive.mzecheru.com/{uuid}"

    # file extension
    file_extension = filepath.name().split(".")[-1]

    # tie chunk urls to link in database
    MdbAPI.create_link(self.user.id, link, uuid, file_extension, mdbfile.chunk_urls)

    # copy
    pyperclip.copy(link)

    # show success message
    messagebox.showinfo("Link Copied", f"Link has been copied to clipboard:\n\n{link}")

  def download_file(self, filepath: FilePath):
    containing_folder = filepath.parent_path()
    mdbfile: MdbFile = MdbAPI.get_file_metadata(self.user.id, containing_folder, filepath.name())

    # create downloads folder if it doesn't exist
    with contextlib.suppress(FileExistsError):
      os.mkdir(".\\downloads\\")

    # create actual file from individual file chunks
    with open(f".\\downloads\\{filepath.name()}", "wb") as f:
      for url in mdbfile.chunk_urls:
        for chunk in DiscordAPI.get_attachment_by_url(url):
          f.write(chunk)
    
    # open containing folder
    os.startfile(".\\downloads\\")
    
    # return filepath
    return f".\\downloads\\{filepath.name()}"

  def rename_file(self, filepath: FilePath, type: str):
    rn_win = ctk.CTkToplevel(self)
    rn_win.title(f"Rename {type}")
    rn_win.geometry("200x200")
    rn_win.iconbitmap("./static/icon.ico")
    rn_win.attributes("-topmost", True)
    rn_win.resizable(False, False)

    ctk.CTkLabel(rn_win, text=f"Enter New {type} Name").pack()
    name_entry = ctk.CTkEntry(rn_win)
    name_entry.pack(pady=10)

    if type == "Folder":
      name_entry.insert(0, filepath.name())
    else:
      name_entry.insert(0, ".".join(filepath.name().split(".")[:-1]))

    old_name_frame = ctk.CTkFrame(rn_win)
    old_name_frame.pack(side=tk.BOTTOM)
    ctk.CTkLabel(old_name_frame, text="Renaming:").pack()
    ctk.CTkLabel(old_name_frame, text=f"/{filepath.name()}/" if type == "Folder" else filepath.name()).pack()

    old_name = name_entry.get()

    # function for enter key
    def enter_key():
      name = name_entry.get().strip()
      if name == old_name: return rn_win.destroy()

      if name and re.match(r"^[a-zA-Z0-9_\-]+$", name):
        extension = ""
        extension = "." + filepath.name().split(".")[-1] if type == "File" else "/"
        userfiles = MdbAPI.get_user_files(self.user.id) if type == "File" else MdbAPI.get_user_folders(self.user.id)

        # rename in list of user files
        index = userfiles.index(filepath.path())
        userfiles[index] = "/".join(userfiles[index].split("/")[:(-2 if type == "Folder" else -1)]) + "/" + name + extension

        # get entry_id of user's filesystem
        entry_id = MdbAPI.get_user_filesystem_entry_by_userid(self.user.id).get("_id")

        # update in DB
        if type == "Folder":
          # update in  api: /users/folders
          MdbAPI.update_user_folders(entry_id, userfiles)

          # update in api: /users/files
          filepaths = MdbAPI.get_user_files(self.user.id)
          for i in range(len(filepaths)):
            fpath: str = filepaths[i]
            if fpath.startswith(filepath.path()):
              filepaths[i] = fpath.replace(filepath.path(), userfiles[index])
          MdbAPI.update_user_files(entry_id, filepaths)

          # get channel entry
          channel: MdbChannel = MdbAPI.get_channel_by_folder_path(self.user.id, filepath.path())

          # update in api: /channels/
          MdbAPI.update_folder_path(
            # get entry id of channel
            channel._id,
            # new folder name
            userfiles[index]
          )

          # update folder path in the discord server channel description
          DiscordAPI.update_channel_description(channel.channel_id, userfiles[index])

          # update in api: /files/folder_path
          # get every file where folder_path = this directory
          for file in MdbAPI.get_files_with_folder_path(self.user.id, filepath.path()):
            file: MdbFile = file
            MdbAPI.update_file_containing_folder(
              # get entry id
              file._id,
              # new folder name
              userfiles[index]
            )
        else:
          # update in api: /users/files
          MdbAPI.update_user_files(entry_id, userfiles)
          
          # update in api: /files/filename
          MdbAPI.update_filename(
            # entry id of file in /files/ api
            MdbAPI.get_file_metadata(self.user.id, filepath.parent_path(), filepath.name())._id,
            # new name
            name
          )

        # rename in the treeview
        iid_of_item = self.filetree_iids.get(filepath.path())
        self.file_tree.item(self.filetree_iids.get(filepath.path()), text=name + (extension if type == "File" else ""), tags=(type.lower(), userfiles[index]))
        del self.filetree_iids[filepath.path()]
        self.filetree_iids[userfiles[index]] = iid_of_item

        rn_win.destroy()
      else:
        messagebox.showerror(f"Rename {type}", f"Invalid {type.lower()} name. {type} name can only contain alphanumeric characters, dashes, and underscores")
        name_entry.delete(0, tk.END)
        name_entry.focus()

    # event listener for enter key
    rn_win.bind("<Return>", lambda event: enter_key())

  def delete_file(self, filepath: FilePath):
    # sourcery skip: extract-method, for-append-to-extend, hoist-similar-statement-from-if, hoist-statement-from-if, list-comprehension, move-assign-in-block
    if filepath.path() == "/": return messagebox.showerror("Delete File", "Cannot delete root folder")

    user_filesystem_entry = MdbAPI.get_user_filesystem_entry_by_userid(self.user.id)
    user_files = user_filesystem_entry.get("files")
    _id = user_filesystem_entry.get("_id")

    if filepath.is_folder():
      user_folders = user_filesystem_entry.get("folders")

      folders_to_remove = []
      files_to_remove = []

      for folder in user_folders:
        if folder.startswith(filepath.path()):
          folders_to_remove.append(folder)
      
      for file in user_files:
        if file.startswith(filepath.path()):
          files_to_remove.append(file)

      # removing has to be done separately otherwise the loops are messed up due to the list changing as it's iterating
      for folder in folders_to_remove:
        user_folders.remove(folder)
      
      for file in files_to_remove:
        user_files.remove(file)

      MdbAPI.update_user_folders(_id, user_folders)
      
      # remove from treeview
      self.file_tree.delete(self.filetree_iids.get(filepath.path()))
      del self.filetree_iids[filepath.path()]
    
    else:
      user_files.remove(filepath.path())
      user_files = MdbAPI.update_user_files(_id, user_files)

      # remove from treeview
      self.file_tree.delete(self.filetree_iids.get(filepath.path()))
      del self.filetree_iids[filepath.path()]

  def new_folder(self, filepath: FilePath):
    if not filepath.is_folder():
      filepath = FilePath(f"/{filepath.parent_path()}/", "folder")

    nf_win = ctk.CTkToplevel(self)
    nf_win.title("Create New Folder")
    nf_win.geometry("200x200")
    nf_win.iconbitmap("./static/icon.ico")
    nf_win.attributes("-topmost", True)
    nf_win.resizable(False, False)

    ctk.CTkLabel(nf_win, text="Enter Folder Name").pack()
    name_entry = ctk.CTkEntry(nf_win)
    name_entry.pack(pady=10)

    path_notice_frame = ctk.CTkFrame(nf_win)
    path_notice_frame.pack(side=tk.BOTTOM)
    ctk.CTkLabel(path_notice_frame, text="Folder will be created in").pack()
    ctk.CTkLabel(path_notice_frame, text=filepath.path() if filepath.path().startswith("/") else f"/{filepath.path()}/").pack()

    # function for enter key
    def enter_key():
      name = name_entry.get().strip()

      if name and re.match(r"^[a-zA-Z0-9_\-]+$", name):
        name += "/"
        new_folder: str = self.create_new_folder(FilePath(filepath.path() + name, "folder"))
        DiscordAPI.create_channel(self.user.id, new_folder)
        nf_win.destroy()
      else:
        messagebox.showerror("Create New Folder", "Invalid folder name. Folder name can only contain alphanumeric characters, dashes, and underscores.")
        name_entry.delete(0, tk.END)
        name_entry.focus()

    # event listener for enter key
    name_entry.bind("<Return>", lambda event: enter_key())

    # event listener for clearing entry
    name_entry.bind("<Control-BackSpace>", lambda event: name_entry.delete(0, tk.END))

  def view_file(self, filepath: FilePath):
      containing_folder = filepath.parent_path()
      mdbfile: MdbFile = MdbAPI.get_file_metadata(self.user.id, containing_folder, filepath.name())

      # create tmp folder if it doesn't exist
      with contextlib.suppress(FileExistsError):
        os.mkdir(".\\tmp\\")

      # create actual file from individual file chunks
      with open(f".\\tmp\\{filepath.name()}", "wb") as f:
        for url in mdbfile.chunk_urls:
          for chunk in DiscordAPI.get_attachment_by_url(url):
            f.write(chunk)

        # make sure there is only one preview frame
      with contextlib.suppress(Exception):
          self.preview_frame.destroy()

      # create viewing frame
      self.preview_frame = ctk.CTkScrollableFrame(master=self.upload_frame, bg_color="#212121", border_color="white", border_width=1, height=1000)
      self.preview_frame.pack(fill="both", expand=True, padx=5, pady=5)

      # create new window
      preview_win = ctk.CTkToplevel(self)
      preview_win.title("View File")
      preview_win.geometry("500x700")
      preview_win.iconbitmap("./static/icon.ico")
      preview_win.attributes("-topmost", True)

      try:
        # filepath
        file = f".\\tmp\\{filepath.name()}"
        # check if file is image
        if imghdr.what(file) is not None:
          ### show image file

          def on_closing():
            preview_win.destroy()
            # delete tmp file
            os.remove(file)

          # on close
          preview_win.protocol("WM_DELETE_WINDOW", on_closing)

          # show image
          img = ImageTk.PhotoImage(Image.open(file))
          preview_win.minsize(img.width(), img.height())
          preview_win.geometry(f"{img.width()}x{img.height()}+0+0")
          preview_image = tk.Label(master=preview_win, image=img)
          preview_image.image = img
          preview_image.pack(padx=5, pady=5)
        elif mimetypes.guess_type(file)[0].startswith('video'):
          videoplayer = TkinterVideo(master=preview_win, scaled=True)
          videoplayer.load(file)
          videoplayer.pack(expand=True, fill="both")
          videoplayer.play()

          def on_closing():
            preview_win.destroy()
            # delete tmp file
            os.remove(file)

          preview_win.protocol("WM_DELETE_WINDOW", on_closing)
        else:
          # show text file
          with open(file, "r") as f:
            preview_label = tk.Label(master=preview_win, text=f.read(), bg="#212121", fg="white")
            preview_label.pack(padx=5, pady=5)
      except UnicodeDecodeError as e:
        # show messagebox popup
        preview_label = tk.Label(master=preview_win, text=file, bg="#212121", fg="white")
        preview_label.pack(padx=5, pady=5)

  def create_new_folder(self, filepath: FilePath) -> str:
    ### rename in tree

    # get parent path
    parent_path = filepath.path()[:-1]
    while not parent_path.endswith("/"):
      parent_path = parent_path[:-1]

    self.filetree_iids[filepath.path()] = self.file_tree.insert(self.filetree_iids.get(parent_path), "end", text=filepath.name(), open=True, tags=("folder", filepath.path()))

    ### rename in db
    user_files_entry = MdbAPI.get_user_filesystem_entry_by_userid(self.user.id)
    user_folders: list = user_files_entry.get("folders")
    user_folders.append(filepath.path())
    MdbAPI.update_user_folders(user_files_entry.get("_id"), user_folders)
    return filepath.path()

  def open_file_tree_contextmenu(self, event):
    # get the item that was right clicked
    item = self.file_tree.identify("item", event.x, event.y)
    
    # select the item
    self.file_tree.selection_set(item)

    # do not open for folders
    if not self.selection_has_tag("folder"):
      self.file_tree_contextmenu.post(event.x_root, event.y_root) # open menu
    else:
      self.file_tree_folder_contextmenu.post(event.x_root, event.y_root) # open menu

  # list of filepaths
  def preview_files_before_uploading(self, files: list[str]):
    try: self.preview_frame.destroy()
    except: pass

    if not files: return

    self.preview_frame = ctk.CTkScrollableFrame(master=self.upload_frame, bg_color="#212121", border_color="white", border_width=1, height=1000)
    self.preview_frame.pack(fill="both", expand=True, padx=5, pady=5)

    self.explorer_selected_files = files
    for file in self.explorer_selected_files:
      try:
        # check if file is image
        if imghdr.what(file) is not None:
          # show image file
          img = ImageTk.PhotoImage(Image.open(file))
          self.preview_image = tk.Label(master=self.preview_frame, image=img)
          self.preview_image.image = img
          self.preview_image.pack(padx=5, pady=5)
        else:
          # show text file
          with open(file, "r") as f:
            self.preview_label = tk.Label(master=self.preview_frame, text=f.read(), bg="#212121", fg="white")
            self.preview_label.pack(padx=5, pady=5)
      except UnicodeDecodeError:
        # show messagebox popup
        self.preview_label = tk.Label(master=self.preview_frame, text=file, bg="#212121", fg="white")
        self.preview_label.pack(padx=5, pady=5)

  def get_explorer_selected_files(self) -> list[str]:
    return self.explorer_selected_files

if __name__ == "__main__":
  ctk.set_appearance_mode("dark")
  ctk.set_default_color_theme("dark-blue")
  Application().mainloop()