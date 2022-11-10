"""
Working client code for a UDP client/server topology
"""
from concurrent.futures import thread
import socket           #Import required modules
from threading import Thread
import threading
import cv2 as cv
import pickle
import hmac
import sys

HOST = "127.0.0.1"      #Hostname of the server
PORT = 10597            #Port currently being used by the server
loggedUser = ''         #String for who is logged in. Empty by default

stop_event = threading.Event()                                              #create thread event
media_stop_event = threading.Event()

print('\nMy media client. Version One.\n')

data = str()                                                            #declare a global string for data sending/receiving
#mediaPlayer = cv.imread()
dataplaceholder = str()
fileToPlay = str()

def listenForMessages():                                                #define our function to talking to the server
    global data                                                         #use the global data being received
    while not stop_event.is_set():                                      #run the thread until the specified event
        data = socketT.recv(1024).decode()                              #dedicate the thread to receiving and printing data
        print(data)

def playMedia():                                                        #Define a function to thread for playing media
    global fileToPlay
    while not media_stop_event.is_set():
        dataplaceholder = socketU.recvfrom(1024)                        #This thread will only be responsible for playing media received as we go further
        print(dataplaceholder[0].decode())
    media_stop_event.clear()
    fileToPlay = ''

def menu():                                                             
    global loggedUser                                                   #use the global data and user for printing
    global data 
    
    print("""Welcome to your media player program. Please use one of the below commands:
Login - Establish conection with the server via a username and password. (Example: "Login 'Username' 'Password'")
Search - Search either the Web or Server database. (Example: "Search Web/Server")
Load - Load the desired media to play next. (Example: "Load Web/Server 'Name of file'")
Recent - List the 10 most recently played files.
Clear - Clear youe recently played list.
Who - List all of the users that are currently logged one at the moment.
Friends - List all of your friends and statuses.
Favorite - Favorite a particular media file. (Example: "Favorite Web/Server 'Name of file'") 
Favorites - List all of your favorited media
Play - Play the desired media (URL, source, etc.)
Logout - Close the program""")

    while(True):                                                        #Menu template
        menuChoice = input().split()     
        match menuChoice[0]:
            case "Login":
                if len(menuChoice) != 3:                                        #error check for correct arguments
                    print("Incorrect use of command. Use 'Login Username Password' format.")                         
                elif loggedUser != '':                                          #if the user is logged in, deny
                    print("Denied. You are already logged in.")
            case "Search":                                                      #Case for searching database/http server
                if len(menuChoice) != 2:
                    print("Incorrect use of command. Use 'Search Location' format.")                         
                else:
                    match menuChoice[1]:
                        case "Web":
                            socketT.sendall(" ".join(menuChoice).encode())
                        case "Server":
                            socketT.sendall(" ".join(menuChoice).encode())
                        case _:
                            print("Please utilize either Web or Server as your location depending on where you want to browse.")
            case "Load":                                                        #Case to load a specified file
                if len(menuChoice) != 3:
                    print("Incorrect use of command. Use 'Load Location Name' format")                         
                elif loggedUser == '':                                          
                    print("Denied. You are not logged in.")
                else:
                    match menuChoice[1]:
                        case "Web":
                            socketT.sendall(" ".join(menuChoice).encode())
                        case "Server":
                            socketT.sendall(" ".join(menuChoice).encode())
                        case _:
                            print("Please utilize either Web or Server as your location.")
            case "Recent":                                                      #Case to list recently played media
                if len(menuChoice) != 1:
                    print("Incorrect use of command. Use 'Recent' format.")                         
                elif loggedUser == '':                                          
                    print("Denied. You are not logged in.")
                else:
                    socketT.sendall(" ".join(menuChoice).encode())
            case "Clear":                                                       #Case to clear recently played media list
                if len(menuChoice) != 1:
                    print("Incorrect use of command. Use 'Clear' format.")                         
                elif loggedUser == '':                                          
                    print("Denied. You are not logged in.")
                else:
                    socketT.sendall(" ".join(menuChoice).encode())
            case "Who":                                                         #Case to list who is online and what they are doing
                if len(menuChoice) != 1:
                    print("Incorrect use of command. Use 'Who' format.")                         
                elif loggedUser == '':                                          
                    print("Denied. You are not logged in.")
                else:
                    socketT.sendall(" ".join(menuChoice).encode())
            case "Friends":                                                     #List online and offline friends and what they are doing
                if len(menuChoice) != 1:
                    print("Incorrect use of command. Use 'Friends' format.")                         
                elif loggedUser == '':                                          
                    print("Denied. You are not logged in.")
                else:
                    socketT.sendall(" ".join(menuChoice).encode())
            case "Favorite":                                                    #List favorited videos
                if len(menuChoice) != 3:
                    print("Incorrect use of command. Use 'Favorite Location Name' format.")                         
                elif loggedUser == '':                                          
                    print("Denied. You are not logged in.")
                else:
                    socketT.sendall(" ".join(menuChoice).encode())
            case "Favorites":                                                   #Add a video to favorited lists
                if len(menuChoice) != 1:
                    print("Incorrect use of command. Use 'Favorites' format.")                         
                elif loggedUser == '':                                          
                    print("Denied. You are not logged in.")
                else:
                    socketT.sendall(" ".join(menuChoice).encode())
            case "Play":                                                        #Play a loaded file (UDP)
                if len(menuChoice) != 1:
                    print("Incorrect use of command. Use 'Play' format.")                         
                elif loggedUser == '':                                          
                    print("Denied. You are not logged in.")
                elif fileToPlay == '':
                    print("Denied. You have not loaded a file to play yet.")
                else:
                    socketU.sendto((menuChoice[0] + fileToPlay).encode(), (HOST, PORT))
                    mediaThreadU.start()       
            case "Logout":                                                      #Case to logout
                print("See you later!")
                socketT.sendall(menuChoice[0].encode())
                stop_event.set()                                            #set thread shutdown events
                media_stop_event.set()
                socketT.shutdown(socket.SHUT_RDWR)                          #shutdown the TCP connection
                socketT.close()                                             #close the TCP socket
                try:                                                        #There is the potential the UDP connection is never established as of now.
                    socketU.shutdown(socket.SHUT_RDWR)
                    socketU.close()
                    mediaThreadU.join()
                except Exception as e:
                    print("Media thread never started/connected.")
                    pass
                listenThreadT.join()                                        #join the threads
                sys.exit()                                                  #exit the program
            case _:
                print("Unkown command. Please use one of the given commands.")

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
