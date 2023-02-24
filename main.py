from PIL import ImageTk, Image
import customtkinter as ctk
import tkinter.ttk as ttk
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import imghdr
from drive_dataclasses import DriveFile, DriveFolder, FilePath, User
from apis import DiscordAPI, MdbAPI

root = DriveFolder("root", [DriveFile("root/bruh.txt"),DriveFile("root/hola.es"),DriveFolder("root/bruh/by", [DriveFile("root/bruh/by/bruh.by")])])

# User's Token
header = {
  'authorization': "NTQ5NDU2MTM4Njk4MjI3NzEy.GrquuR.zbsFWB21L_ZlhM3KBNkkdGCJLEWN1r54EPWdX4",
}

# File
files = {
  "file" : ("./europe.jpg", open("./europe.jpg", 'rb'))
}

# Optional message to send with the picture
payload = {
  "content": "Map of Europe"
}

channel_id = "742932318137876615"

# r = requests.post(f"https://discord.com/api/v9/channels/{channel_id}/messages", data=payload, headers=header, files=files)

class AppPages(ctk.CTk):
  def __init__(self):
    super().__init__()
    self.geometry("500x500")
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
    # TODO: get from api and populate

    # file tree contextmenu
    self.file_tree_contextmenu = tk.Menu(master=self.file_tree_frame, tearoff=False)
    self.file_tree_contextmenu.add_command(label="View", command=lambda: self.view_file(self.get_path()))
    self.file_tree_contextmenu.add_command(label="Download", command=lambda: self.download_file(self.get_path()))
    self.file_tree_contextmenu.add_command(label="Rename", command=lambda: self.rename_file(self.get_path()))
    self.file_tree_contextmenu.add_command(label="Delete", command=lambda: self.delete_file(self.get_path()))
    self.file_tree_contextmenu.add_command(label="New Folder", command=lambda: self.new_folder(self.get_path()))

    # bind right click to file tree contextmenu
    self.file_tree.bind("<Button-3>", self.open_file_tree_contextmenu)

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

  def show_token_entry_screen(self):
    # header
    self.header_frame = ctk.CTkFrame(master=self, bg_color="#2f3136")
    self.header_frame.pack(fill="both", expand=True)

    # header title
    ctk.CTkLabel(master=self.header_frame, text="DiscordDrive", font=("Roboto", 27), fg_color=None).pack(pady=5)

    # enter token frame
    self.enter_token_frame = ctk.CTkFrame(master=self, bg_color="#2f3136")
    self.enter_token_frame.pack(fill="both", expand=True)

    # enter token label
    ctk.CTkLabel(master=self.enter_token_frame, text="Enter Token", font=("Roboto", 15), fg_color=None).pack(pady=5)

    # enter token entry
    self.token_box = ctk.CTkEntry(master=self.enter_token_frame)
    self.token_box.pack(pady=5)

    # enter token button
    self.enter_token_button = ctk.CTkButton(master=self.enter_token_frame, text="Enter", font=("Roboto", 15), command=self.enter_token)
    self.enter_token_button.pack(pady=5)

    # events
    self.token_box.bind("<Return>", lambda event: self.enter_token())
    self.token_box.bind("<Control-BackSpace>", lambda event: self.token_box.delete(0, "end"))

  def invalid_login(self):
    self.username_box.configure(state="normal")
    self.password_box.configure(state="normal")
    self.login_button.configure(state="normal")

    self.username_box.delete(0, "end")
    self.password_box.delete(0, "end")

    self.username_box.focus()

  def invalid_register(self):
    self.username_box.configure(state="normal")
    self.password_box.configure(state="normal")
    self.register_button.configure(state="normal")

    self.username_box.delete(0, "end")
    self.password_box.delete(0, "end")
    
    self.username_box.focus()

class Application(AppPages):
  user: User or None = None
  selected_dir: DriveFolder or None = None

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
        return self.show_token_entry_screen()

      self.user.token = user.get("token")
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
    self.show_token_entry_screen()

  def enter_token(self):
    token = self.token_box.get()
    if not token: return None

    self.token_box.configure(state="disabled")
    self.enter_token_button.configure(state="disabled")

    self.user.set_token(token)
    self.enter_token_frame.destroy()
    self.show_main()

  def get_selected(self):
    return self.file_tree.selection()[0]

  def get_path(self, tag) -> FilePath:
    # the path will be the second given tag
    return FilePath(self.file_tree.item(self.get_selected(), "tags")[0])

  def selection_has_tag(self, tag):
    return tag in self.file_tree.item(self.file_tree.selection()[0], "tags")

  def upload_files(self, files: list):
    if not files: return

    if self.selected_dir is None:
      return messagebox.showerror("Upload Files", "No folder has been selected as the destination for the file upload. Right click on a folder to select it.")

    if messagebox.askokcancel("Upload Files", f"Files will be uploaded to {self.selected_dir.path()}") != "ok": return

    for file in files:
      self.upload_file(file)

    try: self.preview_frame.destroy()
    except: pass

    self.selected_dir = None

  def upload_file(self, file):
    
    print(file)

  def download_file(self, filepath: FilePath):
    pass

  def rename_file(self, filepath: FilePath):
    pass

  def delete_file(self, filepath: FilePath):
    pass

  def new_folder(self, filepath: FilePath):
    pass

  def view_file(self, filepath: FilePath):
    pass

  def drag_file(self, filepath: FilePath):
    pass

  def drop_file(self, filepath: FilePath):
    pass

  def open_file_tree_contextmenu(self, event):
    # get the item that was right clicked
    item = self.file_tree.identify("item", event.x, event.y)
    
    # select the item
    self.file_tree.selection_set(item)

    # do not open for folders
    if not self.selection_has_tag("folder"):
      self.file_tree_contextmenu.post(event.x_root, event.y_root) # open menu
    else:
      self.selected_dir = DriveFolder(self.get_path("folder"))

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
        messagebox.showinfo(title="Note", message=f"Cannot preview file: {file}\n\nThe file can still be uploaded, though.")

  def get_explorer_selected_files(self) -> list[str]:
    return self.explorer_selected_files

if __name__ == "__main__":
  ctk.set_appearance_mode("dark")
  ctk.set_default_color_theme("dark-blue")
  Application().mainloop()