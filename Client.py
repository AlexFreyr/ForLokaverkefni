import socket
import tkinter as tk
from tkinter import ttk

LARGE_FONT = ("Verdana", 12)
MEDIUM_FONT = ("Verdana", 10)


class ClientApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.container = tk.Frame(self)

        self.container.pack(side="top", fill="both", expand=True)

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        frame = StartPage(self.container, self)
        self.frames[StartPage] = frame
        frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def show_user_frame(self, cont, ip, port):
        frame = Game(self.container, self, ip, port)
        self.frames[Game] = frame
        frame.grid(row=0, column=0, sticky="nsew")

        frame = self.frames[cont]
        frame.tkraise()


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        self.controller = controller
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Welcome", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        connect_label = tk.Label(self, text="Connect to server", font=MEDIUM_FONT)
        connect_label.pack()

        textbox = ttk.Entry(self)
        textbox.pack()

        button1 = ttk.Button(self, text="Connect", command=lambda: self.connect_client(textbox.get()))
        button1.pack()

    def connect_client(self, server_address):
        ip, port = server_address.split(':')

        self.controller.show_user_frame(Game, ip, port)


class Game(tk.Frame):
    def __init__(self, parent, controller, ip, port):
        self.ip = ip
        self.port = port
        self.controller = controller
        self.s = socket.socket()
        tk.Frame.__init__(self, parent)
        
        if self.connect_client():
            label = tk.Label(self, text="Connected to server ", font=LARGE_FONT)
            label.pack(pady=10, padx=10)

        button1 = ttk.Button(self, text="Back to home", command=lambda: controller.show_frame(StartPage))
        button1.pack()

    def connect_client(self):
        try:
            self.s.connect((self.ip, int(self.port)))
            self.controller.show_user_frame(Game)
            return True
        except socket.error as error:
            error_label = tk.Label(self, text=error, font=MEDIUM_FONT, fg="red")
            error_label.pack()
            return False

app = ClientApp()

app.title("Guessing game")
app_width, app_height = 720, 240
screen_width, screen_height = app.winfo_screenwidth(), app.winfo_screenheight()
start_width, start_height = (screen_width / 2) - (app_width / 2), (screen_height / 2) - (app_height / 2)
app.geometry("%dx%d+%d+%d" % (app_width, app_height, start_width, start_height))

app.mainloop()
