"""
Note: Same with the current server, I am currently working on transferring the recusrion menu into a switch/do while.
"""
import socket           #Import required modules
from threading import Thread
import threading
import sys

HOST = "127.0.0.1"      #Hostname of the server
PORT = 10597            #Port currently being used by the server
loggedUser = ''         #String for who is logged in. Empty by default

print('\nMy chat room client. Version Two.\n')

data = str()                                                            #declare a global string for data sending/receiving

def listenForMessages():                                                #define our function to thread
    global data                                                         #use the global data being received
    while not stop_event.is_set():                                      #run the thread until the specified event
        data = s.recv(1024).decode()                                    #dedicate the thread to receiving and printing data
        print(data)

def menu():                                                             #same as V1 create our user menu function
    global loggedUser                                                   #use the global data and user for printing
    global data 
    menuChoice = input().split()                                        #seperate the user inputs

    if menuChoice[0] == "login":                                        #if the user is logging in    
        if len(menuChoice) != 3:                                        #error check for correct arguments
            print("Incorrect use of command. Use 'login Username Password' format")                         
        elif loggedUser != '':                                          #if the user is logged in, deny
            print("Denied. You are already logged in.")
        else:                                               
            s.sendall(" ".join(menuChoice).encode())                    #send information to server
            data = s.recv(1024).decode()                                #receive data since thread hasnt started yet
            print(data)       
            if data == "login confirmed":
                loggedUser = menuChoice[1]                              #set the user logged in
                t.start()                                               #start the thread      
        menu()                                                          #recursively call the menu
    elif menuChoice[0] == "newuser":                                    #if the user is creating a new entry
        if len(menuChoice) != 3:                                        #error check for correct arguments
            print("Incorrect use of command. Use 'newuser Username Password' format")   
        elif loggedUser != '':                                          #check for logged in user
            print("Denied. You are already logged in.")
        else:
            if len(menuChoice[1]) >= 3 and len(menuChoice[1]) <= 32:    #check for username bounds  
                if len(menuChoice[2]) >= 4 and len(menuChoice[2]) <= 8: #check for password 
                    s.sendall(" ".join(menuChoice).encode())            #We have to listen since the thread isnt started yet
                    data = s.recv(1024).decode()
                    print(data)            
                else:                                                   #error messages
                    print("Password is out of bounds. Length should be between 4 and 8 characters.")    
            else:
                print("Username is out of bounds. Length should be between 3 and 32 characters.")      
        menu()
    elif menuChoice[0] == "send":                                       #if user is sending to a specific user       
        if loggedUser != '':                                            #If the user is logged in
            hold = " ".join(menuChoice)                                 #concat the message back
            hold = hold[5:]                                             #strip the 'send ' message
            if 1 <= len(hold) <= 256:
                s.sendall(" ".join(menuChoice).encode())                #send the message if in bounds      
            else:                                                       #error message otherwise
                print("Denied. Please only send messages of character length 1 to 256.")       
        else:
            print("Denied. Please login first.")            
        menu()
    elif menuChoice[0] == "send" and menuChoice[1] == "all":            #if user is sending to everyone  
        if loggedUser != '':                                            #check for logged in user
            hold = " ".join(menuChoice)                                 #concat the message back
            hold = hold[9:]                                             #strip the 'send all ' characters for message length                
            if 1 <= len(hold) <= 256:         
                s.sendall(" ".join(menuChoice).encode())                #send the message if it's in bounds                
            else:                                                       #error message otherwise
                print("Denied. Please only send messages of character length between 1 and 256.")       
        else:
            print("Denied. Please login first.")            
        menu()
    elif menuChoice[0] == "who":                                        #if the user wants to know who is logged on
        if loggedUser != '':                                            #if the user is logged on
            s.sendall(menuChoice[0].encode())                           #send choice to server 
        else:                                                           #error message otherwise
            print("Invalid request. You are not currently logged in.")      
        menu()
    elif menuChoice[0] == "logout":                                     #if the user wants to log out
        if loggedUser != '':                                            #check if logged in
            s.sendall(menuChoice[0].encode())                           #send to server
            stop_event.set()                                            #set thread shutdown event
            s.shutdown(socket.SHUT_RDWR)                                #shutdown the socket
            s.close()                                                   #close the socket
            t.join()                                                    #join the threads
            sys.exit()                                                  #exit the program
        else:                                                           #error message otherwise
            print("Invalid request. You are not currently logged in.")      
            menu()
    else:
        print("You must use the commands provided")         
        menu()

stop_event = threading.Event()                                          #create thread event

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:        #create a socket named s using IPV4 address and connect with TCP
        s.connect((HOST, PORT))                                         #connect on provided host/port
        t = Thread(target = listenForMessages)                          #initialize thread with function 'listenForMessages'
        t.daemon = True                                                 #tell the thread to be a daemon
        menu()
except Exception as e:                                                  #end the program if broken
    sys.exit()
