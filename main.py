import dataclasses
from typing import Optional
import requests
import customtkinter as ctk

mdb_header = {
  "Authorization": "dac5523e-2be9-4d8a-afe4-492b5bf297fa"
}

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


@dataclasses.dataclass
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
    requests.put(f"https://mdb.mzecheru.com/api/24/main/users/{self.id}", json={ "token": token }, headers=mdb_header)


class Application(ctk.CTk):
  user: User or None = None

  def __init__(self):
    super().__init__()
    self.geometry("500x500")
    self.title("DiscordDrive")
    self.resizable(False, False)
    self.show_login()

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
    self.password_box.bind("<Return>", lambda event: self.login())

  def login(self) -> bool or None:
    username = self.username_box.get()
    password = self.password_box.get()

    if not username or not password: return None

    self.username_box.configure(state="disabled")
    self.password_box.configure(state="disabled")
    self.login_button.configure(state="disabled")
    
    # get password of user with given username
    user = requests.get(f"https://mdb.mzecheru.com/api/24/main/users/?username={username}", headers=mdb_header).json()

    # invalid username
    if not user:
      return self.invalid_login()

    actual_password = user[0].get("password")

    # check if password is correct
    if password == actual_password:
      self.login_frame.destroy()
      self.user = User(user[0].get("username"), user[0].get("password")).set_id(user[0].get("_id"))

      if user[0].get("token") is None:
        return self.show_token_entry_screen()

      self.user.token = user[0].get("token")
      self.show_main()
    else:
      self.invalid_login()

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

  def register(self):  # sourcery skip: use-named-expression
    username = self.username_box.get()
    password = self.password_box.get()

    if not username or not password: return None

    self.username_box.configure(state="disabled")
    self.password_box.configure(state="disabled")
    self.register_button.configure(state="disabled")

    # check if username is taken
    user = requests.get(f"https://mdb.mzecheru.com/api/24/main/users/?username={username}", headers=mdb_header).json()

    if user:
      return self.invalid_register()

    # create user
    self.user = User(username=username, password=password)
    res = requests.post("https://mdb.mzecheru.com/api/24/main/users/", json={ "username": username, "password": password }, headers=mdb_header).json()
    self.user.set_id(res.get("_id"))

    self.register_frame.destroy()
    self.show_token_entry_screen()

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
    self.password_box.bind("<Return>", lambda event: self.register())

  def show_main(self):
    pass

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

  def enter_token(self):
    token = self.token_box.get()

    if not token: return None

    self.token_box.configure(state="disabled")
    self.enter_token_button.configure(state="disabled")

    self.user.set_token(token)
    self.enter_token_frame.destroy()
    self.show_main()


if __name__ == "__main__":
  ctk.set_appearance_mode("dark")
  ctk.set_default_color_theme("dark-blue")
  Application().mainloop()