import tkinter as tk
import json
import socket
import random
from threading import Thread
from tkinter import ttk

LARGE_FONT = ("Verdana", 12)
MEDIUM_FONT = ("Verdana", 1import tkinter as tk
import json
import socket
import random
from threading import Thread
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

    def show_server_frame(self, cont, ip, port):
        frame = Server(self.container, self, ip, port)
        self.frames[Server] = frame
        frame.grid(row=0, column=0, sticky="nsew")

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

        self.controller.show_server_frame(Server, ip, port)


class Server(tk.Frame):
    def __init__(self, parent, controller, ip, port):
        self.ip = ip
        self.port = port
        self.controller = controller
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.questions_generated = []  # Questions will be stored in this list
        self.clients = []  # Client connection will be stored in this list

        tk.Frame.__init__(self, parent)

        server = Thread(target=self.start_server)
        server.start() # Server starts on new thread

        label = tk.Label(self, text="Server started at " + ip + ":" + port, font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(self, text="Close server", command=self.close_server)
        button1.pack()

    def start_server(self):
        self.sock.bind((self.ip, int(self.port)))
        self.sock.listen(1)

        try:
            conn1, addr1 = self.sock.accept()
            accept_label1 = ttk.Label(self, text="First client connected", font=MEDIUM_FONT)
            accept_label1.pack()
            client1 = Thread(target=self.client_handler, args=(conn1, addr1, ))
            client1.start() # First client is set on a new thread
            self.clients.append([conn1, addr1])

            conn2, addr2 = self.sock.accept()
            accept_label2 = ttk.Label(self, text="Both clients are connected", font=MEDIUM_FONT)
            accept_label2.pack()
            client2 = Thread(target=self.client_handler, args=(conn2, addr2, ))
            client2.start() # Second client is set on a new thread
            self.clients.append([conn2, addr2])

            accept_label1.destroy()

            for x in self.clients:
                x[0].send("start".encode('utf-8'))  # Send both clients to start the game

            self.game_controller()  # Generate the questions that game will use

            questions = json.dumps(self.questions_generated)  # Serialize the list
            for x in self.clients:
                x[0].send(questions.encode('utf-8'))  # Send both clients the questions

        except socket.error as error:
            print(error)

    def game_controller(self):
        questions = [["ISP stands for"], ["International Service Provider", "Internet Service Provider", "Internet Service Presenter", "None of the above"], [1]], \
                    [["WWW stands for"], ["World Worm Web", "World Wide Web", "World Word Web", "None of the above"], [1]], \
                    [["A Bit stands for"], ["Binary Digit", "Binary Data", "Binary Deci", "None of the above"], [0]], \
                    [["Collection of 1024 bytes"], ["1MB", "1KB", "1TB", "1GB"], [1]], \
                    [["Which of the following is a storage device?"], ["Hard Disk", "Floppy Disk", "USB Disk", "All of the above"], [3]], \
                    [["If the B in a BST stands for Binary, what does the S stand for?"], ["Super", "Storage", "Search", "Sign"], [2]], \
                    [["In C++, what punctuation marks are used to bound the beginning & end of code blocks?"], ["{ & }", "% & %", "( & )", "None of the above"], [1]], \
                    [["The IEEE 802.3 standard is often referred to by which term?"], ["Internet", "Computer", "Ethernet", "Cable"], [2]], \
                    [["Files with .py extensions are associated with what programming language?"], ["Perl", "Python", "C++", "PHP"], [1]], \
                    [["In the abbreviation 'USB' what does the 'B' stand for"], ["Bycycle", "Buffer", "Bus", "Bug"], [1]], \
                    [["Red Hat, Ubuntu, Debian etc. are distributions of which Operating System"], ["Linux", "AIX", "Symbian", "OS X"], [0]], \
                    [["What does an SSL certificate do?"], ["Tracks your web travels", "Validates website authenticity", "Tells website about you", "Blocks spam from webpages"], [1]], \
                    [["Which US Defense project is considered the precursor to the Internet"], ["Fibrenet", "ARPANET", "InNet", "Intranet"], [1]], \
                    [["In C, what is the index of the first element of any array"], ["10", "-1", "1", "0"], [3]], \
                    [["Which of these is a statement from SQL"], ["GREP", "SELECT", "PIPE", "COMPILE"], [1]], \
                    [["Which is an example of infix notation?"], ["S + 3 4 =", "S = + 2 2", "S = 3 + 3", "S = 5 6 +"], [2]], \
                    [["Which of these is a term associated with TCP/IP?"], ["Clip", "Nail", "Envelope", "Packet"], [3]]

        question_len = len(questions)
        random_numbers = random.sample(range(0, question_len - 1), 10)

        for x in range(0, 10):
            self.questions_generated.append(questions[random_numbers[x]])

    def client_handler(self, conn, addr):  # This handles all of the clients
        question_counter = 0
        score = 0
        self.game_controller()

        data = conn.recv(1024).decode('utf-8')  # Waiting for the client to finish

        if data == "finished":
            data = conn.recv(1024).decode('utf-8')
            score = data
        for x in self.clients:
            if x[0] != conn:
                print("ok")
                x[0].send(str(score).encode('utf-8'))  # Send the other player the score


    def close_server(self):
        self.sock.close()
        self.controller.show_frame(StartPage)


app = ClientApp()

app.title("Guessing game server")
app_width, app_height = 720, 240
screen_width, screen_height = app.winfo_screenwidth(), app.winfo_screenheight()
start_width, start_height = (screen_width / 2) - (app_width / 2), (screen_height / 2) - (app_height / 2)
app.geometry("%dx%d+%d+%d" % (app_width, app_height, start_width, start_height))

def on_closing():
    app.destroy()
    quit()

app.protocol("WM_DELETE_WINDOW", on_closing)
app.mainloop()
0)


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

    def show_server_frame(self, cont, ip, port):
        frame = Server(self.container, self, ip, port)
        self.frames[Server] = frame
        frame.grid(row=0, column=0, sticky="nsew")

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

        self.controller.show_server_frame(Server, ip, port)


class Server(tk.Frame):
    def __init__(self, parent, controller, ip, port):
        self.ip = ip
        self.port = port
        self.controller = controller
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.questions_generated = []  # Questions will be stored in this list
        self.clients = []  # Client connection will be stored in this list

        tk.Frame.__init__(self, parent)

        server = Thread(target=self.start_server)
        server.start() # Server starts on new thread

        label = tk.Label(self, text="Server started at " + ip + ":" + port, font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(self, text="Close server", command=self.close_server)
        button1.pack()

    def start_server(self):
        self.sock.bind((self.ip, int(self.port)))
        self.sock.listen(1)

        try:
            conn1, addr1 = self.sock.accept()
            accept_label1 = ttk.Label(self, text="First client connected", font=MEDIUM_FONT)
            accept_label1.pack()
            client1 = Thread(target=self.client_handler, args=(conn1, addr1, ))
            client1.start() # First client is set on a new thread
            self.clients.append([conn1, addr1])

            conn2, addr2 = self.sock.accept()
            accept_label2 = ttk.Label(self, text="Both clients are connected", font=MEDIUM_FONT)
            accept_label2.pack()
            client2 = Thread(target=self.client_handler, args=(conn2, addr2, ))
            client2.start() # Second client is set on a new thread
            self.clients.append([conn2, addr2])

            accept_label1.destroy()

            for x in self.clients:
                x[0].send("start".encode('utf-8'))  # Send both clients to start the game

            self.game_controller()  # Generate the questions that game will use

            questions = json.dumps(self.questions_generated)  # Serialize the list
            for x in self.clients:
                x[0].send(questions.encode('utf-8'))  # Send both clients the questions

        except socket.error as error:
            print(error)

    def game_controller(self):
        questions = [["ISP stands for"], ["International Service Provider", "Internet Service Provider", "Internet Service Presenter", "None of the above"], [1]], \
                    [["WWW stands for"], ["World Worm Web", "World Wide Web", "World Word Web", "None of the above"], [1]], \
                    [["A Bit stands for"], ["Binary Digit", "Binary Data", "Binary Deci", "None of the above"], [0]], \
                    [["Collection of 1024 bytes"], ["1MB", "1KB", "1TB", "1GB"], [1]], \
                    [["Which of the following is a storage device?"], ["Hard Disk", "Floppy Disk", "USB Disk", "All of the above"], [3]], \
                    [["If the B in a BST stands for Binary, what does the S stand for?"], ["Super", "Storage", "Search", "Sign"], [2]], \
                    [["In C++, what punctuation marks are used to bound the beginning & end of code blocks?"], ["{ & }", "% & %", "( & )", "None of the above"], [1]], \
                    [["The IEEE 802.3 standard is often referred to by which term?"], ["Internet", "Computer", "Ethernet", "Cable"], [2]], \
                    [["Files with .py extensions are associated with what programming language?"], ["Perl", "Python", "C++", "PHP"], [1]], \
                    [["In the abbreviation 'USB' what does the 'B' stand for"], ["Bycycle", "Buffer", "Bus", "Bug"], [1]], \
                    [["Red Hat, Ubuntu, Debian etc. are distributions of which Operating System"], ["Linux", "AIX", "Symbian", "OS X"], [0]], \
                    [["What does an SSL certificate do?"], ["Tracks your web travels", "Validates website authenticity", "Tells website about you", "Blocks spam from webpages"], [1]], \
                    [["Which US Defense project is considered the precursor to the Internet"], ["Fibrenet", "ARPANET", "InNet", "Intranet"], [1]], \
                    [["In C, what is the index of the first element of any array"], ["10", "-1", "1", "0"], [3]], \
                    [["Which of these is a statement from SQL"], ["GREP", "SELECT", "PIPE", "COMPILE"], [1]], \
                    [["Which is an example of infix notation?"], ["S + 3 4 =", "S = + 2 2", "S = 3 + 3", "S = 5 6 +"], [2]], \
                    [["Which of these is a term associated with TCP/IP?"], ["Clip", "Nail", "Envelope", "Packet"], [3]]

        question_len = len(questions)
        random_numbers = random.sample(range(0, question_len - 1), 10)

        for x in range(0, 10):
            self.questions_generated.append(questions[random_numbers[x]])

    def client_handler(self, conn, addr):  # This handles all of the clients
        question_counter = 0
        score = 0
        self.game_controller()

        data = conn.recv(1024).decode('utf-8')  # Waiting for the client to finish

        if data == "finished":
            data = conn.recv(1024).decode('utf-8')
            score = data
        for x in self.clients:
            if x[0] != conn:
                print("ok")
                x[0].send(str(score).encode('utf-8'))  # Send the other player the score


    def close_server(self):
        self.sock.close()
        self.controller.show_frame(StartPage)


app = ClientApp()

app.title("Guessing game server")
app_width, app_height = 720, 240
screen_width, screen_height = app.winfo_screenwidth(), app.winfo_screenheight()
start_width, start_height = (screen_width / 2) - (app_width / 2), (screen_height / 2) - (app_height / 2)
app.geometry("%dx%d+%d+%d" % (app_width, app_height, start_width, start_height))

def on_closing():
    app.destroy()
    quit()

app.protocol("WM_DELETE_WINDOW", on_closing)
app.mainloop()
