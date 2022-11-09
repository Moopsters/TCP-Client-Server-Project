"""
First implementation of a UDP media server
Ultimate goal will be to have a running server for users to request various forms of media downloads
"""
import socket           #import the required modules
from threading import Thread
import threading
import cv2 as cv
import pickle
import hmac
import sys

HOST = "127.0.0.1"      #Host ip assignment
PORT = 10597            #Random unused port
MAXCLIENTS = 5

currentUsers = {}
sendingMedia = []

stop_event = threading.Event()   

print("\nMy media server. Version One.\n")

socketT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                       #create a socket named s using IPV4 with a UDP and TCP connection
socketU = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
socketT.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)                     #set the socket to not block after a connection
socketU.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  

socketT.bind((HOST, PORT))                                                        #bind the socket using the host/port given 
socketU.bind((HOST, PORT))      
socketT.listen(MAXCLIENTS)                                                        #listen for the max amount of clients given
socketU.listen(MAXCLIENTS)

def sendMedia():
    global currentUsers                                                     #use the global logged in users dictionary
    try:
        while not stop_event:
            client_socket, client_address = socketU.accept()
            sendingMedia.append(client_socket)
            print(f"Will send 'media' to {client_address} via UDP here")
            stop_event.set()
    except KeyboardInterrupt:                                               
        pass
    

def listenForClients(cs):                                                   #define our thread function
    global currentUsers                                                     
    try:
        while True:                                                         #while the thread is running
            try:
                data = cs.recv(1024).decode()                               #receive user input on the specified thread
                userInput = data.split()                                    #parse the data
            except Exception as e:
                for userName, client_socket in currentUsers.copy().items(): #if the connection is closed
                    if client_socket == cs:                                 #find the connection of the thread
                        del currentUsers[userName]                          #remove them from the dictionary of logged in users
                break
            if userInput != []:                                             #if the user actually sent data
                match userInput[0]:
                    case "Play":
                        mediaThread.start()
                    case _:
                        print("User did not send usable data")
    except KeyboardInterrupt:                                               #stop the server with interrupt
        if currentUsers != {}:                                                  #close all the sockets
            for key, cs in currentUsers.copy().items():
                cs.close()                                                         #close the socket
        
        chatThread.join()    
        sys.exit()

try:
    while True:                                                             #while there is a connection
        client_socket, client_address = socketT.accept()                    #accept connections

        print(f"Connected by {client_address}")                             #maintain server log

        chatThread = Thread(target = listenForClients, args = (client_socket,))      #create thread with 'listenForClients" function and send socket info as arg
        mediaThread = Thread(target = sendMedia)

        chatThread.daemon = True                                                     #set thread to daemon
        mediaThread.daemon = True

        chatThread.start()                                                           #start the thread
except KeyboardInterrupt:                                                   #if interrupted
    if currentUsers != {}:                                                  #close all the sockets
        for key, cs in currentUsers.copy().items():
            cs.close()
    socketT.close()
