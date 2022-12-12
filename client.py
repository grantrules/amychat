import socket, tkinter
from threading import Thread

# client
client = None


HOST_ADDRESS = "rps.mehh.net"
HOST_PORT = 8080

def send_message_to_server(cmd, msg=""):
    client.send(bytes(cmd + " " + msg + "\n","utf-8"))
    if cmd == "exit":
        client.close()
        window.destroy()
    print("Sending")

cWindow = tkinter.Tk()
cWindow.title("Connect")

bFrame = tkinter.Frame(cWindow)
createLobby = tkinter.IntVar(cWindow)
ra = tkinter.Radiobutton(bFrame, text="Start a lobby", variable=createLobby, value=0)
rb = tkinter.Radiobutton(bFrame, text="Join a lobby", variable=createLobby, value=1)
lobby = tkinter.Entry(bFrame)
ra.pack(side=tkinter.LEFT)
rb.pack(side=tkinter.LEFT)
lobby.pack(side=tkinter.LEFT)

# top frame


topFrame = tkinter.Frame(cWindow)
hostLabel = tkinter.Label(topFrame, text="Host: ").pack(side=tkinter.LEFT)
enterHost = tkinter.Entry(topFrame)
enterHost.insert(0,HOST_ADDRESS)
enterHost.pack(side=tkinter.LEFT)
nameLabel = tkinter.Label(topFrame, text="Name: ").pack(side=tkinter.LEFT)
enterName = tkinter.Entry(topFrame)
enterName.pack(side=tkinter.LEFT)
connectButton = tkinter.Button(topFrame, text = "Connect", command=lambda: connect())
connectButton.pack(side=tkinter.LEFT)
topFrame.pack(side=tkinter.TOP)


bFrame.pack(side=tkinter.BOTTOM)



#

window = tkinter.Tk()
window.title("Client")
#game frame
gameFrame = tkinter.Frame(window)
lineLabel = tkinter.Label(gameFrame, text="Game").pack()

things = ["Rock", "Paper", "Scissors"]

def mkbtn(thing, i):
    tkinter.Button(gameFrame, text = thing, command=lambda: play(i)).pack(side=tkinter.LEFT)

class ReadyButton():
    isReady = False
    def __init__(self, frame, cmd):
        self.btn =tkinter.Button(frame, text="Ready", command=lambda: self.ready())
        self.btn.pack(side=tkinter.BOTTOM)
        self.cmd = cmd
    def ready(self): 
        self.cmd("ready")
        self.isReady = not self.isReady
        self.btn.config(relief=tkinter.SUNKEN if self.isReady else tkinter.RAISED)



readyBtn = ReadyButton(gameFrame, send_message_to_server)

for (i, thing)  in enumerate(things):
    mkbtn(thing, i)

gameFrame.pack(side=tkinter.TOP)

#display frame
displayFrame = tkinter.Frame(window)
lineLabel = tkinter.Label(displayFrame, text="***").pack()
scrollBar = tkinter.Scrollbar(displayFrame)
scrollBar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
tkinterDisplay = tkinter.Text(displayFrame, height=20, width=55)
tkinterDisplay.pack(side=tkinter.LEFT, fill=tkinter.Y, padx=(5, 0))
tkinterDisplay.tag_config("tag_your_message", foreground="purple")
scrollBar.config(command=tkinterDisplay.yview)
tkinterDisplay.config(yscrollcommand=scrollBar.set, background="#ebe6fa", highlightbackground="grey", state="disabled")
displayFrame.pack(side=tkinter.TOP)

# bottom frame
bottomFrame = tkinter.Frame(window)
tkinterMessage = tkinter.Text(bottomFrame, height=1, width=55)
tkinterMessage.pack(side=tkinter.LEFT, padx=(5, 12), pady=(5, 10))
tkinterMessage.config(highlightbackground="grey", state="disabled")
tkinterMessage.bind("<Return>", lambda event: get_messages(tkinterMessage.get("1.0", tkinter.END)))
bottomFrame.pack(side=tkinter.BOTTOM)



def play(move):
    send_message_to_server("play", str(move))

def connect():
    if len(enterName.get()) < 1:
        tkinter.messagebox.showerror(title="Error :(", message="Enter your name.")
    else:
        username = enterName.get()
        host = enterHost.get()
        connect_to_server(host, username)
        if createLobby.get() == 0:
            send_message_to_server("create")
        else:
            send_message_to_server("join", lobby.get())


def connect_to_server(host, name):
    global client, HOST_PORT
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, HOST_PORT))
        send_message_to_server(name)

        enterName.config(state=tkinter.DISABLED)
        connectButton.config(state=tkinter.DISABLED)
        tkinterMessage.config(state=tkinter.NORMAL)

        Thread(target=receive_message_from_server, args=(client,"m")).start()
    except Exception as e:
        print(e)
        tkinter.messagebox.showerror(title="Error :(", message="Can't connect to host: " + HOST_ADDRESS + " on port: " + str(HOST_PORT) + ".")


def receive_message_from_server(sck, m):
    while True:
        from_server = sck.recv(4096)

        if not from_server: break

        texts = tkinterDisplay.get("1.0", tkinter.END).strip()
        tkinterDisplay.config(state=tkinter.NORMAL)
        if len(texts) < 1:
            tkinterDisplay.insert(tkinter.END, from_server.decode("utf-8"))
        else:
            tkinterDisplay.insert(tkinter.END, "\n\n" + from_server.decode("utf-8"))

        tkinterDisplay.config(state=tkinter.DISABLED)
        tkinterDisplay.see(tkinter.END)

    sck.close()
    window.destroy()


def get_messages(msg):
    msg = msg.replace('\n', '')
    texts = tkinterDisplay.get("1.0", tkinter.END).strip()

    tkinterDisplay.config(state=tkinter.DISABLED)

    send_message_to_server("msg", msg)

    tkinterDisplay.see(tkinter.END)
    tkinterMessage.delete('1.0', tkinter.END)




window.mainloop()
