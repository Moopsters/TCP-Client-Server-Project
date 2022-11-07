"""
Note I used if/elif for the server. I am currently moving it over to a switch statement/do while 
"""
import socket           #import the required modules
from threading import Thread
import sys

HOST = "127.0.0.1"      #Host ip assignment
PORT = 10597            #Random unused port
MAXCLIENTS = 5


with open(sys.argv[1]) as f:                                                #read the users into a table from a file
    userTable = f.read().splitlines()
f.close()                                                                   #close the file

for x in range(len(userTable)):                                             #loop through the table
    userTable[x] = userTable[x].lstrip(userTable[x][0]).rstrip(userTable[x][-1])    #strip the parenthesis off the file input

currentUsers = {}                                                           #create a dictionary for logged in users

print("\nMy chat room server. Version Two.\n")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                       #create a socket named s using IPV4 with a TCP connection
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
                if userInput[0] == 'login':                                 #if they are logging in
                    for x in range(len(userTable)):                         #loop through the username/passwords
                        userTableCheck = userTable[x]
                        userTableCheck = userTableCheck.split(", ")         #format the users and passwords for checking

                        if userInput[1] == userTableCheck[0] and userInput[2] == userTableCheck[1]: #if the input is in the file
                            if userInput[1] in currentUsers:                #check if they are already logged in
                                cs.sendall('Denied. User is already logged in on another platform'.encode())
                            else:                                           #if they aren't logged in already
                                currentUsers[f"{userInput[1]}"] = cs        #add the user to the logged in user dictionary
                                cs.sendall('login confirmed'.encode())      #send the user confirmation

                                for userName, client_socket in currentUsers.items():    #send every user that 'user' logged in
                                    if client_socket != cs:
                                        client_socket.send(f"{userInput[1]} joins".encode())

                                print(f"{userName} login.")                 #maintain log on server side
                                break       
                        elif x == len(userTable) - 1:                       #else the username/password combo doesn't exist
                            cs.sendall('Denied. User name or password incorrect'.encode())  #error message
                elif userInput[0] == 'newuser':                             #if the user wants to create a new user
                    for x in range(len(userTable)):                         #essentially opposite of login
                        userTableCheck = userTable[x]           
                        userTableCheck = userTableCheck.split(", ")         #format

                        if userInput[1] == userTableCheck[0]:               #if the username already exists in file
                            cs.sendall('Denied. user account already exists.'.encode()) #error message
                            break
                        elif x == len(userTable) - 1:                       #else it doesnt exist
                            f = open(sys.argv[1], "a")                      #open the file
                            f.write(f"\n({userInput[1]}, {userInput[2]})")  #add the new username/password combo in format
                            f.close()                                       #close the file
                            userTable.append(f"{userInput[1]}, {userInput[2]}") #add the user to the current open user table
                            print(f"New user account {userInput[1]} created.")  #maintain log on server side
                            cs.sendall('New user account created. Please login.'.encode())  #send user confirmation
                elif userInput[0] == 'logout':                              #if the user is loggin out
                    userName_list = list(currentUsers.keys())               #get current user dictionary keys
                    socket_list = list(currentUsers.values())               #get current user dictionary values
                    senderName = socket_list.index(cs)                      #get the key of the user
                    for userName, client_socket in currentUsers.copy().items(): #loop through the dictionary
                        if client_socket != cs:                             #send every other user this user left
                            client_socket.sendall(f"{userName_list[senderName]} left".encode())
                        else:
                            del currentUsers[userName]                      #remove the user from the current user dictionary
                elif userInput[0] == 'who':                                 #if the user wants to know who is online
                    hold = []                                               #create temp list
                    for userName, client_socket in currentUsers.copy().items():
                        hold.append(userName)                               #append the keys of the current user dictionary
                    cs.sendall(", ".join(hold).encode())                    #send the list in string format
                elif userInput[0] == 'send' and userInput[1] == 'all':      #if the user wants to send all
                    userName_list = list(currentUsers.keys())               #get current user dictionary keys
                    socket_list = list(currentUsers.values())               #get current user dictionary values
                    senderName = socket_list.index(cs)                      #get the key of the user
                    hold = " ".join(userInput)                              #concat the message back
                    hold = hold[9:]                                         #strip the useless 'send all ' statement
                    for userName, client_socket in currentUsers.copy().items():
                        if client_socket != cs:                             #loop through the current user dictionary 
                            client_socket.sendall(f"{userName_list[senderName]}: {hold}".encode())  #send the message and user who sent it
                elif userInput[0] == 'send':                                #same as send all command
                    userName_list = list(currentUsers.keys())
                    if userInput[1] in userName_list:                       #only send if user if logged in
                        socket_list = list(currentUsers.values())
                        senderName = socket_list.index(cs)
                        hold = " ".join(userInput)
                        hold = hold[6 + len(userInput[1]):]                 #strip useless 'send userName ' statement
                        currentUsers[f"{userInput[1]}"].sendall(f"{userName_list[senderName]}: {hold}".encode())    #send the message
                        print(f"{userName_list[senderName]} (to {userInput[1]}): {hold}")
                    else:
                        cs.sendall(f"{userInput[1]} is either offline or doesnt exist yet.".encode()) #error message if not logged in
    except KeyboardInterrupt:                                               #stop the server with interrupt
        if currentUsers != {}:                                                  #close all the sockets
            for key, cs in currentUsers.copy().items():
                cs.close()                                                         #close the socket
        t.join()    
        sys.exit()                                                          #end the program
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
