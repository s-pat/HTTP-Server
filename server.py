import sys
import time
import datetime
import mimetypes
import os
from socket import *

# Setting the HTTP error messages in variables
HTTP304 = "HTTP/1.1 304 Not Modified"
HTTP404 = "HTTP/1.1 404 File Not Found"
HTTP200 = "HTTP/1.1 200 OK"

serverIP = "127.0.0.1"  # any local IP address
serverPort = 12000
dataLen = 1000000


def message(filename):
    if(os.path.exists(filename)):
        msg = HTTP200
    else:
        msg = HTTP404
    return str(msg)


def getFileName(data):
    fileName = data.split()[1].split("/")[1]

    return str(fileName)
# Getting today's date


def date():
    time = datetime.datetime.utcnow()
    Date = time.strftime("%a, %d %b %Y %H:%M:%S GMT")
    return str(Date)
# Determining a file's modification time


def lastModTime(filename):
    secs = os.path.getmtime(filename)
    t = time.gmtime(secs)
    last_mod_time = time.strftime("%a, %d %b %Y %H:%M:%S GMT")
    return str(last_mod_time)
# Getting the file contents


def fileContents(filename):
    #file = open(filename, "r")
    #fileContents = file.read()
    with open(filename) as file:
        fileContents = file.read()
    return str(fileContents)
# Getting the type and encoding of the file


def contentType(filename):
    fileType = mimetypes.guess_type(filename)[0]
    encoding = "UTF-8"
    content_Type = fileType+"; charset="+encoding+"\r\n"+"\r\n"
    return str(content_Type)
# Getting the length of the file


def contentLength(filename):
    length = os.path.getsize(filename)
    return str(length)


def getLastModTime(clientRequest):
    lastModTime = clientRequest.split("\n")[2].split(": ")[1].split("\r")[0]
    return str(lastModTime)


# Create a TCP "welcoming" socket.
serverSocket = socket(AF_INET, SOCK_STREAM)
# Assign IP address and port number to socket
serverSocket.bind((serverIP, serverPort))

# Listen for incoming connection requests
serverSocket.listen(1)

print('The server is ready to receive on port: '+str(serverPort))

# loop forever listening for incoming connection requests on "welcoming" socket
while True:
    # Accept incoming connection requests, and allocate a new socket or data communication
    connectionSocket, address = serverSocket.accept()
    print("Socket created for client "+address[0]+", "+str(address[1]))

    # Recieve and print the client data in bytes from "data" socket
    clientRequest = connectionSocket.recv(dataLen).decode()
    print("Client sent request")
    if("If-Modified-Since:" in clientRequest):
        # Get filename from client request
        file_name = getFileName(clientRequest)
        # Get last mod time from client request
        error_message = message(file_name)
        if("404" in error_message):
            serverResponse = error_message + "\r\nDate: " + date() + "\r\n" + "\r\n"
        else:
            clientLastModTime = getLastModTime(clientRequest)
            # Get last mod time of the file
            fileLastModTime = lastModTime(file_name)
            # compare both last modtime
            # if mod times are same then print 304
            if(clientLastModTime == fileLastModTime):
                serverResponse = HTTP304 + "\r\nDate: " + date() + "\r\n" + "\r\n"
            # else send the updated file to the client
            else:
                serverResponse = HTTP200 + "\r\nDate: " + date() + "\r\n" + "\r\nLast-Modified: "+lastModTime(file_name)+"\r\nContent-Length: " + \
                    contentLength(file_name) + "\r\nContent_Type: " + \
                    contentType(file_name)+"\r\n"+"\r\n" + \
                    fileContents(file_name)
    else:
        file_name = getFileName(clientRequest)
        error_message = message(file_name)
        serverResponse = ""
        if ("200" in error_message):
            serverResponse = error_message + "\r\nDate: " + date() + "\r\nLast-Modified: " + lastModTime(file_name) + "\r\nContent-Length: " + \
                contentLength(file_name) + "\r\nContent_Type: " + \
                contentType(file_name)+"\r\n"+"\r\n" + fileContents(file_name)
        if("404" in error_message):
            serverResponse = error_message + "\r\nDate: " + date() + "\r\n"+"\r\n"
        print("Server replied to client's request")
    # Echo back to client
    connectionSocket.send(serverResponse.encode())
    connectionSocket.close()
