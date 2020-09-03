# ESP8266WebServer

This is a very lightweight web server for MicroPython on ESP8266.It only accept GET requests.It adopts the programming style of  ESP8266WebServer library in ESP8266 Arduino Core.This make it suitable for serving REST API.The original code was inspired from the project [Controlling a GPIO through an ESP8266-based web server](https://lab.whitequark.org/notes/2016-10-20/controlling-a-gpio-through-an-esp8266-based-web-server/).

## Installation

Just upload ESP8266WebServer.py to your ESP8266 board and you're done.

## Usage

To use ESP8266WebServer.py library, you should:

1. Write functions as handlers for each path you'd like to serve contents. 

1. Start the server by calling begin(). 

1. Regsiter the handlers you just prepared by calling onPath().

1. You can also uploading HTML files onto somewhere in the filesystem and settnig the document path by calling setDocPath().

1. Call handleClient() repeatly to process requests.

### Documents and Templates

With setDocPath(), you can spcicified the path for all html files. For examples, if you call setDocPath('www'), and put index.html into /www, you can browse the file with 'http://server_ip/www/index.html. 

If you put a file with suffix '.p.html', the server would do formatting processing before output the content. You should first call setTplData() with a dictionary before accessing any template file, the server uses the elements in the dictionary to replacing all the formatting string in the template file.

If you access the document path without filename, the server would try to find out if there's a index.html or index.p.html file existed, and output the file. 

## Function reference

### begin(port)

Start the server at specified *port*.

### onPath(path, handler)

Register *handler* for processing request with matching *path* 

### setDocPath(path)

Specified the directory in the filesystem containing all the HTML files.

### setTplData(dic)

Specified the dictionary for template file. `dic` sould be a dictionary with all keys are string and contains all the names in replacing fields in all the template files.

### handleClient()

Check for new request and call corresponding handler to process it.

## Examples

You can upload www directory and index.p.html to "/" on ESP8266 board and run TestWebServer.py to see how it works.

TestWebServer.py will show its own IP address through serial monitor.Just open your browser and connect it to http://serverIP:8899 or http://serverIP:8899/index.p.html, you'll get the main page that can turn on/off the buildin led on ESP8266 board. The main page also demonstrate the template file usage. 

You can also open http://serverip:8899/www/index.html or http://serverip:8899/www/ to view alternative version of controlling page that use AJAX to asynchronously turn on/off led.

You can use http://serverip:8899/switch to switch led on/off led directly. Or you can use http://serverip:8899/cmd?led=on to turn the led on and http://serverip:8899/cmd?led=off to turn the led off.
