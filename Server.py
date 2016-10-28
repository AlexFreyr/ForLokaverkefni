import socket
import threading
import tkinter as tk
from tkinter import ttk

LARGE_FONT = ("Verdana", 12)
MEDIUM_FONT = ("Verdana", 10)


class ClientApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        frame = StartPage(container, self)
        self.frames[StartPage] = frame
        frame.grid(row=0, column=0, sticky="nsew")

        frame = Server(container, self, 'test', 'test')
        self.frames[Server] = frame
        frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        self.controller = controller
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Welcome", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        connect_label = tk.Label(self, text="Enter your IP and port that clients will connect to (ex. 192.168.1.5:9999)", font=MEDIUM_FONT)
        connect_label.pack()

        textbox = ttk.Entry(self)
        textbox.pack()

        button1 = ttk.Button(self, text="Start", command=lambda: self.start_server(textbox.get()))
        button1.pack()

    def start_server(self, server_address):
        ip, port = server_address.split(':')

        self.controller.show_frame(Server)


class Server(tk.Frame):
    def __init__(self, parent, controller, ip, port):
        self.ip = ip
        self.port = port
        self.controller = controller
        self.s = socket.socket()
        tk.Frame.__init__(self, parent)
        # self.start_server()
        label = tk.Label(self, text="Server started at " + ip + ":" + port, font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(self, text="Close server", command=lambda: self.close_server())
        button1.pack()

    def start_server(self):
        self.s.bind((self.ip, self.port))
        self.s.listen(1)

        try:
            fd, addr = self.s.accept()
            print("Connection was accepted")
        except socket.error as error:
            print(error)

    def close_server(self):
        self.s.close()
        self.controller.show_frame(StartPage)


app = ClientApp()

app.title("Guessing game")
app_width, app_height = 720, 240
screen_width, screen_height = app.winfo_screenwidth(), app.winfo_screenheight()
start_width, start_height = (screen_width / 2) - (app_width / 2), (screen_height / 2) - (app_height / 2)
app.geometry("%dx%d+%d+%d" % (app_width, app_height, start_width, start_height))

app.mainloop()
