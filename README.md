# ESP8266WebServer
This is a very lightweight web server for MicroPython on ESP8266.It only aceept GET requests.It adopt the progrmming style of of ESP8266WebServer library in ESP8266 Arduino Core.This make it suitable for serving REST API.The original code was inspired from the project [Controlling a GPIO through an ESP8266-based web server](https://lab.whitequark.org/notes/2016-10-20/controlling-a-gpio-through-an-esp8266-based-web-server/).

## Installation
Just upload ESP8266WebServer.py to your ESP8266 board and you're done.

## Usage
To use ESP8266WebServer.py library, you should first writing functions as handler for each path you mean to serve content. Then you start the server by calling begin(port).You can then regsiter the handlers you just prepared by calling onPath().You can also uploading HTML files onto somewhere in the filesystem and settnig the document path by calling setDocPath().After that, you just need to call handleClient() repeatly to process requests.

## Function reference

### begin(port)

Start the server at specified *port*.

### onPath(path, handler)

Register *handler* for processing request with matching *path* 

### setDocPath(path)

Specified the director in the filesystem containing all the HTML files.

### handleClient()

Check for new request and call corresponding handler to process it.

## Examples

You can upload www director to "/" on ESP8266 board and run TestWebServer.py to see how it works.TestWebServer.py will show its own IP address Open browser and connect to http://serverIP:8899. You'll get the main page that can turn on/off the buildin led on ESP8266 board.You can also open http://serverip:8899/www/index.html to view alternative version of control page that use AJAX to asynchronously turn on/off led.
