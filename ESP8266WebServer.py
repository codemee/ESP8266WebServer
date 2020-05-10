"""A simple HTTP server that only accept GET request
It adopt the programming style of ESP8266WebServer 
library in ESP8266 Arduino Core
"""

import network
import machine
import socket
import uselect
import os

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Use for checking a new client connection
poller = uselect.poll()
# Dict for registed handlers of all paths
handlers = {}
# Function of handler for request not found
notFoundHandler = None
# The path to the web documents on MicroPython filesystem
docPath = "/"
# Data for template
tplData = {}

def begin(port):
    """Function to start http server
    """
    global server, poller
    server.bind(('0.0.0.0', port))
    server.listen(1)
    # Register for checking new client connection
    poller.register(server, uselect.POLLIN)

def close():
    """Function to stop http server
    """
    poller.unregister(server)
    server.close()

def handleClient():
    """Check for new client connection and process the request
    """
    global server, poller
    # Note:don't call poll() with 0, that would randomly cause
    # reset with "Fatal exception 28(LoadProhibitedCause)" message
    res = poller.poll(1)
    if res:  # There's a new client connection
        (socket, sockaddr) = server.accept()
        handle(socket)
        socket.close()

def __sendPage(socket, filePath):
    """Send the file as webpage to client
    """
    try:
        f = open(filePath, "rb")
        while True:
            data = f.read(64)
            if (data == b""):
                break
            socket.write(data)
        f.close()
    except Exception as e:
        print(e)


def err(socket, code, message):
    """Respong error meesage to client
    """
    socket.write("HTTP/1.1 " + code + " " + message + "\r\n\r\n")
    socket.write("<h1>" + message + "</h1>")

def ok(socket, code, msg):
    """Response successful message or webpage to client
    """
    socket.write("HTTP/1.1 " + code + " OK\r\n\r\n")
    if __fileExist(msg):
        filePath = msg
        __sendPage(socket, filePath)
    else:
        socket.write(msg)

def __fileExist(path):
    """Check for file existence
    """
    print(path)
    try:
        stat = os.stat(path)
        # stat[0] bit 15 / 14 -> file/dir
        if stat[0] & 0x8000 == 0x8000: # file
            print("Found.")
            return True
        else:  # Dir
            return False
    except:
        print("Not Found.")
        return False

def handle(socket):
    """Processing new GET request
    """
    global docPath, handlers
    currLine = str(socket.readline(), 'utf-8')
    request = currLine.split(" ")
    if len(request) != 3: # Discarded if it's a bad header
        return
    (method, url, version) = request
    if "?" in url: # Check if there's query string?
        (path, query) = url.split("?", 2)
    else:
        (path, query) = (url, "")
    args = {}
    if query: # Parsing the querying string
        argPairs = query.split("&")
        for argPair in argPairs:
            arg = argPair.split("=")
            args[arg[0]] = arg[1]
    while True: # Read until blank line after header
        header = socket.readline()
        if header == b"":
            return
        if header == b"\r\n":
            break

    # Check for supported HTTP version
    if version != "HTTP/1.0\r\n" and version != "HTTP/1.1\r\n":
        err(socket, "505", "Version Not Supported")
    elif method != "GET": # Only accept GET request
        err(socket, "501", "Not Implemented")
    elif path in handlers: # Check for registered path
        handlers[path](socket, args)
    #elif not path.startswith(docPath): # Check for path to any document
    #    err(socket, "400", "Bad Request")
    else:
        filePath = path
        # find the file
        if not __fileExist(filePath):
            filePath = path + ("index.html" if path.endswith("/") else "/index.html")
            # find index.html in the path
            if not __fileExist(filePath):
                filePath = path + ("index.p.html" if path.endswith("/") else "/index.p.html")
                # find index.p.html in the path
                if not __fileExist(filePath):
                    if notFoundHandler:
                        notFoundHandler(socket)
                    else:
                        err(socket, "404", "Not Found")
                    return
            
        # Responds the header first
        socket.write("HTTP/1.1 200 OK\r\n\r\n")
        # Responds the file content
        if filePath.endswith(".p.html"):
            print("template file.")
            f = open(filePath, "r")
            for l in f:
                socket.write(l.format(**tplData))
            f.close()
        else:
            __sendPage(socket, filePath)

def onPath(path, handler):
    """Register handler for processing request of specified path
    """
    global handlers
    handlers[path] = handler
    
def onNotFound(handler):
    """Register handler for processing request of not found path
    """
    global notFoundHandler
    notFoundHandler = handler

def setDocPath(path):
    """Set the path to documents' directory
    """
    global docPath
    docPath = path

def setTplData(data):
    """Set data for template
    """
    global tplData
    tplData = data
