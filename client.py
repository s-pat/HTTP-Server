import sys
import time
import datetime
import os
from socket import*
# Setting HTTP messages in variables
HTTP304 = "HTTP/1.1 304 Not Modified"
HTTP404 = "HTTP/1.1 404 File Not Found"
HTTP200 = "HTTP/1.1 200 OK"

# Get the URL as a command line argument
argv = sys.argv
URL = argv[1]  # url format: localhost:12000/filename.html


def cacheCheck():
    if(os.path.exists("cache.txt")):
        return True
    else:
        return False


def cacheLastModTime():
    if(cacheCheck()):
        secs = os.path.getmtime("cache.txt")
        t = time.gmtime(secs)
        last_mod_time = time.strftime("%a, %d %b %Y %H:%M:%S GMT")
    else:
        last_mod_time = "N/A"
    return str(last_mod_time)


def getContents(serverResponse):
    contents = serverResponse.split("\n", 6)[6]
    return str(contents)


def createCacheFile():
    file = open("cache.txt", "w+")
    file.close()


def editCacheFile(contents):
    with open("cache.txt", "w") as file:
        file.write(contents)


# Parsing the URL to get the host, port, and file name
host = str(URL.split("/")[0].split(":")[0])
port = int(URL.split("/")[0].split(":")[1])
fileName = str(URL.split("/")[1])

GET = "GET /"+fileName+" HTTP/1.1\r\nHOST:"+URL.split("/")[0]+"\r\n"+"\r\n"
conditionalGET = "GET /"+fileName+" HTTP/1.1\r\nHOST:" + \
    URL.split("/")[0]+"\r\nIf-Modified-Since: " + \
    cacheLastModTime()+"\r\n"+"\r\n"
# Print data to be sent

#data = fileName

# Create TCP client socket.
clientSocket = socket(AF_INET, SOCK_STREAM)

# Create TCP connection to server
clientSocket.connect((host, port))

# Send data through TCP connection
if(cacheCheck()):
    print(conditionalGET)
    clientSocket.send(conditionalGET.encode())
    dataEcho = clientSocket.recv(4096)
    serverResponse = dataEcho.decode()
    print(serverResponse)
    if(HTTP304 in serverResponse):
        quit()
    elif (HTTP404 in serverResponse):
        quit()
    else:
        # Get filecontents
        fileContents = getContents(serverResponse)
        # Modify the cache file
        editCacheFile(fileContents)
        quit()
else:
    print(GET)
    clientSocket.send(GET.encode())
    # Recieve the server response
    dataEcho = clientSocket.recv(4096)  # count =  dataLength
    serverResponse = dataEcho.decode()
    # Display the server response as an output
    print(serverResponse)
    if(HTTP404 in serverResponse):
        quit()
    # Get the file contents
    fileContents = getContents(serverResponse)
    # create the cache file
    createCacheFile()
    # Modify the cache file
    editCacheFile(fileContents)
    # Close the client socket
    clientSocket.close()
