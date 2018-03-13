# A simple HTTP server that only accept GET request
# It adopt the programming style of ESP8266WebServer 
# library in ESP8266 Arduino Core

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
# The path to the web documents on MicroPython filesystem
docPath = "/"

# Function to start http server
def begin(port):
  global server
  server.bind(('0.0.0.0', port))
  server.listen(1)
  # Register for checking new client connection
  poller.register(server, uselect.POLLIN)

# Check for new client connection and process the request
def handleClient():
  global server
  # Note:don't call poll() with 0, that would randomly cause
  # reset with "Fatal exception 28(LoadProhibitedCause)" message
  res = poller.poll(1)
  if res:  # There's a new client connection
    (socket, sockaddr) = server.accept()
    handle(socket)
    socket.close()

# Respong error meesage to client
def err(socket, code, message):
  socket.write("HTTP/1.1 " + code + " " + message + "\r\n\r\n")
  socket.write("<h1>" + message + "</h1>")

# Response succesful message to client
def ok(socket, code, msg):
  socket.write("HTTP/1.1 " + code + " OK\r\n\r\n")
  socket.write(msg)

# Processing new GET request
def handle(socket):
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
  elif method == "GET": # Only accept GET request
    if path.find(docPath) == 0: # Check for path to any document
      try:
        os.stat(path) # Check for file existence
        # Response header first
        socket.write("HTTP/1.1 200 OK\r\n\r\n")
        # Response the file content
        f = open(path, "rb")
        while True:
          data = f.read(64)
          if (data == b""):
            break
          socket.write(data)
        return
      except: # Can't find the file specified in path
        err(socket, "404", "Not Found")
    elif path in handlers: # Check for registered path
      handlers[path](socket, args)
    else:
      err(socket, "400", "Bad Request")
  else:
    err(socket, "501", "Not Implemented")

# Register handler for processing request fo specified path
def onPath(path, handler):
  global handlers
  handlers[path] = handler

# Set the path to documents' directory
def setDocPath(path):
  global docPath
  docPath = path
