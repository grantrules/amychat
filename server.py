import random, string
import socket
import threading

from game import Game


# server
server = None
HOST_ADDRESS = "0.0.0.0"
HOST_PORT = 8080



players = []
rooms = {}

def start_server():
    global server, HOST_ADDRESS, HOST_PORT

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST_ADDRESS, HOST_PORT))
    server.listen(5)

    threading._start_new_thread(accept_clients, (server, " "))
    print("Host: " + HOST_ADDRESS)
    print("Port: " + str(HOST_PORT))
    while True:
        pass


def accept_clients(the_server, y):
    while True:
        client, address = the_server.accept()

        player = { 'connection': client, 'address': address, 'ready': False, 'play': -1 }
        players.append(player)

        threading._start_new_thread(send_receive_client_message, (client, address))

def find_player(client_connection, players):
    return next(filter(lambda p: p['connection'] == client_connection, players))

def send_receive_client_message(client_connection, client_ip):
    global server, players
    client_msg = " "

    player = find_player(client_connection, players)
 

    while True:
        data = client_connection.recv(4096)
        if data:

            client_msgs = data.decode("utf-8")
            cmds = client_msgs.split("\n")
            for client_msg in cmds:
                print(client_msg)
                if 'username' not in player:
                    # should normalize this
                    player['username'] = client_msg
                    send(client_connection, "welcome Hi %s. Type exit to leave." % player['username'])
                    print("Joined: %s" % player['username'])
                elif data == "exit": break
                else:
                    [cmd, *stuff] = client_msg.split(" ", 1)
                    stuff = None if len(stuff) == 0 else stuff[0]
                    if cmd == "ready":
                        player['ready'] = not player['ready']

                        roomPlayers = list(filter(lambda p: 'room' in p and player['room'] == p['room'], players))
                        playersReady = len(list(filter(lambda p: p['ready'], roomPlayers)))

                        if playersReady > 1 and playersReady == len(players):
                            sendRoom(player['room'], "All ready. Game starting")
                            rooms[player['room']].startGame(roomPlayers)
                            for p in roomPlayers:
                                p['ready'] = False
                        else:
                            sendRoom(player['room'], "%s players ready" % str(playersReady))


                    if cmd == "msg":
                        for p in players:
                            if p['connection'] != client_connection and p['room'] == player['room']:
                                p['connection'].send(bytes("%s -> %s" % (player['username'], stuff), "utf-8")) 
                    if cmd == "create":
                        room = genRoomKey()
                        player['room'] = room
                        rooms[room] = Game()
                        send(client_connection,"joined %s" % room)
                    if cmd == "join":
                        room = stuff
                        player['room'] = room
                        sendRoom(room, "%s has joined" % player['username'])
                    if cmd == "play":
                        play = int(stuff)
                        if play in range(0,3):
                            player['play'] = play
                        sendRoom(player['room'], "%s has played" % (player['username']))
                        

    print("Left %s" % player['name'])
    players.remove(player)
    client_connection.close()

def sendRoom(room, msg):
    global players
    for p in players:
        if 'room' in p and p['room'] == room:
            send(p['connection'], msg)

def send(client,payload):
    client.send(bytes(payload+"\n","utf-8"))

def get_client_by_connection(client_list, current_client):
    index = 0
    for connected in client_list:
        if connected == current_client:
            break
        index = index + 1

    return index


def genRoomKey(num=5):
    return ''.join(random.choice(string.ascii_uppercase) for i in range(0,num))

start_server()