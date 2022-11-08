"""
Working client code for a UDP client/server topology
"""
import socket           #Import required modules
from threading import Thread
import threading
import cv2 as cv
import sys

HOST = "127.0.0.1"      #Hostname of the server
PORT = 10597            #Port currently being used by the server
loggedUser = ''         #String for who is logged in. Empty by default

print('\nMy media client. Version One.\n')

data = str()                                                            #declare a global string for data sending/receiving
mediaPlayer = cv.imread()

def listenForMessages():                                                #define our function to talking to the server
    global data                                                         #use the global data being received
    while not stop_event.is_set():                                      #run the thread until the specified event
        data = socketT.recv(1024).decode()                                    #dedicate the thread to receiving and printing data
        print(data)

def playMedia():                                                        #Define a function to thread for playing media
    global mediaPlayer
    while not stop_event.is_set():
        mediaPlayer = socketU.recv(1024).decode()                       #This thread will only be responsible for playing media received as we go further

def menu():                                                             
    global loggedUser                                                   #use the global data and user for printing
    global data 
    
    print(""""Welcome to your media player program. Please use one of the below commands:
                Start - Establish conection with the server via a username and password (Example: "Start 'Username' 'Password'")
                Play - Play the desired media (URL, source, etc.)
                Logout - Close the program""")

    while(True):                                                        #Menu template
        menuChoice = input().split()     
        match menuChoice[0]:
            case "Start":
                listenThreadT.start()
                socketT.sendall(" ".join(menuChoice).encode())
            case "Play":
                socketU.connect((HOST, PORT))                               #Initially using same port as the TCP connection. Will change if this doesnt work.
                socketU.sendall(" ".join(menuChoice).encode())
            case "Logout":
                print("See you later!")
                socketT.sendall(menuChoice[0].encode())
                stop_event.set()                                            #set thread shutdown event
                socketT.shutdown(socket.SHUT_RDWR)                          #shutdown the TCP connection
                socketT.close()                                             #close the TCP socket
                try:                                                        #There is the potential the UDP connection is never established as of now.
                    socketU.shutdown(socket.SHUT_RDWR)
                    socketU.close()
                    mediaThreadU.join()
                except Exception as e:
                    pass
                listenThreadT.join()                                        #join the threads
                sys.exit()                                                  #exit the program
            case _:
                print("Unkown command. Please use one of the given commands")

stop_event = threading.Event()                                              #create thread event

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketT:       #create a socket named s using IPV4 address and connect with TCP
        socketU = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socketT.connect((HOST, PORT))                                        #connect on provided host/port
        listenThreadT = Thread(target = listenForMessages)                   #initialize thread with function 'listenForMessages'
        mediaThreadU = Thread(target = playMedia)
        listenThreadT.daemon = True                                          #tell the thread to be a daemon
        mediaThreadU.daemon = True
        menu()
except Exception as e:                                                  #end the program if broken
    sys.exit()
