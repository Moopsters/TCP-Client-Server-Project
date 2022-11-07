# TCP-Client-Server-Project
Side project implementation of basic client server manipulation of data. 

Note: The current implementation utilizes a Username/Password text file that is formatted as (Username, Password)

The implementation at the moment supports send user, send all, who, newuser, login, and logout functionality. A user should only be able to log in on one
running instance of the server. Otherwise, they will not be allowed to login on multiple instances of client applications.

send user: Send a message to a specified user if they are logged on at the time of request.<br />
send all: Send a message to all users that are currently logged one (minus the sender).<br />
who: List all of the users that are currently logged on in the chatroom.<br />
login: Log in using verified username/password based on server knowledge.<br />
newuser: Create a new user, add it to the username/password text, and add it to the current running server.<br />
logout: Logout from the server, and send a message to all users that that user is now offline.<br />
