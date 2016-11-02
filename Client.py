import socket
import json
import tkinter as tk
import time
from tkinter import ttk
from threading import Thread

LARGE_FONT = ("Verdana", 12)
MEDIUM_FONT = ("Verdana", 10)


class ClientApp(tk.Tk):import socket
import json
import tkinter as tk
import time
from tkinter import ttk
from threading import Thread

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
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.questions = []
        self.question = None
        self.answer1, self.answer2, self.answer3, self.answer4 = None, None, None, None
        self.counter = 0
        self.score = 0
        tk.Frame.__init__(self, parent)

        if self.connect_client():
            self.label = tk.Label(self, text="Connected to server ", font=LARGE_FONT)
            self.label.pack(pady=10, padx=10)

            wait = Thread(target=self.wait_for_start_signal)  # Wait for the game to start
            wait.start()  # Start a new thread that waits for the game to start

        self.button1 = ttk.Button(self, text="Back to home", command=lambda: controller.show_frame(StartPage))
        self.button1.pack()

    def wait_for_start_signal(self):
        data = None
        while data != "start":
            data = self.s.recv(1024).decode('utf-8')
            if not data:
                break
        self.init_game()

    def init_game(self):
        self.label.destroy()
        self.button1.destroy()

        question_data = self.s.recv(8192).decode('utf-8')  # Hopefully this will return a list
        question_data = json.loads(question_data)  # De-serialize the list
        self.questions = question_data
        Thread(target=self.game_display).start()

        print(self.questions)
        while True:
            data = self.s.recv(1024).decode('utf-8')
            opponent_text = "Your opponent finished with a score of: " + data
            opponent_score = tk.Label(self, text=opponent_text, font=LARGE_FONT)
            opponent_score.pack()

    def game_display(self):

        self.question = tk.Label(self, text=self.questions[self.counter][0][0], font=LARGE_FONT)

        self.answer1 = ttk.Button(self, text=self.questions[self.counter][1][0],
                                command=lambda: self.answer_question(0))
        self.answer2 = ttk.Button(self, text=self.questions[self.counter][1][1],
                                command=lambda: self.answer_question(1))
        self.answer3 = ttk.Button(self, text=self.questions[self.counter][1][2],
                                command=lambda: self.answer_question(2))
        self.answer4 = ttk.Button(self, text=self.questions[self.counter][1][3],
                                command=lambda: self.answer_question(3))

        self.question.pack()
        self.answer1.pack()
        self.answer2.pack()
        self.answer3.pack()
        self.answer4.pack()

    def answer_question(self, btn_nr):
        answer = self.questions[self.counter][2][0]
        self.counter += 1
        if answer == btn_nr:
            self.score += 1
            #  Increase player score

        self.question.destroy()
        self.answer1.destroy()
        self.answer2.destroy()
        self.answer3.destroy()
        self.answer4.destroy()

        if self.counter < 10:
            self.game_display()
        else:
            self.game_finish()

    def get_rival_score(self):
        data = None
        data_recv = False
        rival_score = None
        while not data_recv:
            data = self.s.recv(1024).decode('utf-8')
            rival_score = data
            data_recv = True
        rival_text = "Your opponent score: " + rival_score
        display_rival_score = tk.Label(self, text=rival_text, font=LARGE_FONT)
        display_rival_score.pack()


    def game_finish(self):
        self.s.send("finished".encode('utf-8'))
        self.s.send(str(self.score).encode('utf-8'))

        score_text = "Your score: " + str(self.score)
        display_score = tk.Label(self, text=score_text, font=LARGE_FONT)
        display_score.pack()
        Thread(target=self.get_rival_score).start()


    def connect_client(self):
        try:
            self.s.connect((self.ip, int(self.port)))
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

def on_closing():
    app.destroy()
    quit()

app.protocol("WM_DELETE_WINDOW", on_closing)
app.mainloop()

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
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.questions = []
        self.question = None
        self.answer1, self.answer2, self.answer3, self.answer4 = None, None, None, None
        self.counter = 0
        self.score = 0
        tk.Frame.__init__(self, parent)

        if self.connect_client():
            self.label = tk.Label(self, text="Connected to server ", font=LARGE_FONT)
            self.label.pack(pady=10, padx=10)

            wait = Thread(target=self.wait_for_start_signal)  # Wait for the game to start
            wait.start()  # Start a new thread that waits for the game to start

        self.button1 = ttk.Button(self, text="Back to home", command=lambda: controller.show_frame(StartPage))
        self.button1.pack()

    def wait_for_start_signal(self):
        data = None
        while data != "start":
            data = self.s.recv(1024).decode('utf-8')
            if not data:
                break
        self.init_game()

    def init_game(self):
        self.label.destroy()
        self.button1.destroy()

        question_data = self.s.recv(8192).decode('utf-8')  # Hopefully this will return a list
        question_data = json.loads(question_data)  # De-serialize the list
        self.questions = question_data
        Thread(target=self.game_display).start()

        print(self.questions)
        while True:
            data = self.s.recv(1024).decode('utf-8')
            print(data)

    def game_display(self):

        self.question = tk.Label(self, text=self.questions[self.counter][0][0], font=LARGE_FONT)

        self.answer1 = ttk.Button(self, text=self.questions[self.counter][1][0],
                                command=lambda: self.answer_question(0))
        self.answer2 = ttk.Button(self, text=self.questions[self.counter][1][1],
                                command=lambda: self.answer_question(1))
        self.answer3 = ttk.Button(self, text=self.questions[self.counter][1][2],
                                command=lambda: self.answer_question(2))
        self.answer4 = ttk.Button(self, text=self.questions[self.counter][1][3],
                                command=lambda: self.answer_question(3))

        self.question.pack()
        self.answer1.pack()
        self.answer2.pack()
        self.answer3.pack()
        self.answer4.pack()

    def answer_question(self, btn_nr):
        answer = self.questions[self.counter][2][0]
        self.counter += 1
        if answer == btn_nr:
            self.score += 1
            #  Increase player score

        self.question.destroy()
        self.answer1.destroy()
        self.answer2.destroy()
        self.answer3.destroy()
        self.answer4.destroy()

        if self.counter < 10:
            self.game_display()
        else:
            self.game_finish()

    def get_rival_score(self):
        data = None
        data_recv = False
        rival_score = None
        while not data_recv:
            data = self.s.recv(1024).decode('utf-8')
            rival_score = data
            data_recv = True
        rival_text = "Your opponent score: " + rival_score
        display_rival_score = tk.Label(self, text=rival_text, font=LARGE_FONT)
        display_rival_score.pack()


    def game_finish(self):
        self.s.send("finished".encode('utf-8'))
        self.s.send(str(self.score).encode('utf-8'))

        score_text = "Your score: " + str(self.score)
        display_score = tk.Label(self, text=score_text, font=LARGE_FONT)
        display_score.pack()
        Thread(target=self.get_rival_score).start()


    def connect_client(self):
        try:
            self.s.connect((self.ip, int(self.port)))
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

def on_closing():
    app.destroy()
    quit()

app.protocol("WM_DELETE_WINDOW", on_closing)
app.mainloop()
