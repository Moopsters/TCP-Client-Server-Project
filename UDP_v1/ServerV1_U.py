"""
First implementation of a UDP media server
Ultimate goal will be to have a running server for users to request various forms of media downloads
"""
import socket           #import the required modules
from threading import Thread
import cv2 as cv
import sys

HOST = "127.0.0.1"      #Host ip assignment
PORT = 10597            #Random unused port
MAXCLIENTS = 5

currentUsers = {} 

print("\nMy media server. Version One.\n")

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)                       #create a socket named s using IPV4 with a UDP connection
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)                     #set the socket to not block after a connection

s.bind((HOST, PORT))                                                        #bind the socket using the host/port given       
s.listen(MAXCLIENTS)                                                        #listen for the max amount of clients given

def listenForClients(cs):                                                   #define our thread function
    global currentUsers                                                     #use the global logged in users dictionary
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
            if userInput != []:                                             #if the user actually sent usable data
                pass
    except KeyboardInterrupt:                                               #stop the server with interrupt
        if currentUsers != {}:                                                  #close all the sockets
            for key, cs in currentUsers.copy().items():
                cs.close()                                                         #close the socket
        t.join()    
        sys.exit()
        
try:
    while True:                                                             #while there is a connection
        client_socket, client_address = s.accept()                          #accept connections

        print(f"Connected by {client_address}")                             #maintain server log

        t = Thread(target = listenForClients, args = (client_socket,))      #create thread with 'listenForClients" function and send socket info as arg
        t.daemon = True                                                     #set thread to daemon
        t.start()                                                           #start the thread
except KeyboardInterrupt:                                                   #if interrupted
    if currentUsers != {}:                                                  #close all the sockets
        for key, cs in currentUsers.copy().items():
            cs.close()
    s.close()
