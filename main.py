import ESP8266WebServer
import network
import machine

GPIO_NUM = 2 # Builtin led (D4)
# Get pin object for controlling builtin LED
pin = machine.Pin(GPIO_NUM, machine.Pin.OUT)
pin.on() # Turn LED off (it use sinking input)

# Dictionary for template file
ledData = {
    "title":"Remote LED",
    "color":"red",
    "status":"Off",
    "switch":"on"
}

# Update information
def updateInfo(socket):
    global ledData, color, status, switch
    ledData["color"] = "red" if pin.value() else "green"
    ledData["status"] = "Off" if pin.value() else "On"
    ledData["switch"] = "on" if pin.value() else "off"
    ESP8266WebServer.ok(
        socket,
        "200",
        ledData["status"])

def handleStop(socket):
    ESP8266WebServer.ok(
        socket,
        "200",
        "stopped")
    running = False
    ESP8266WebServer.close()

def handlePost(socket, args, method, contenttype, content):
    ESP8266WebServer.ok(
        socket,
        "200",
        method+" "+contenttype+" "+content.decode('UTF-8'))

# Handler for path "/cmd?led=[on|off]"
def handleCmd(socket, args):
    if 'led' in args:
        if args['led'] == 'on':
            pin.off()
        elif args['led'] == 'off':
            pin.on()
        updateInfo(socket)
    else:
        ESP8266WebServer.err(socket, "400", "Bad Request")

# handler for path "/switch"
def handleSwitch(socket, args):
    pin.value(not pin.value()) # Switch back and forth
    updateInfo(socket)

# Start the server @ port 8899
# ESP8266WebServer.begin(8899)
ESP8266WebServer.begin() # use default 80 port

# Register handler for each path
# ESP8266WebServer.onPath("/", handleRoot)
ESP8266WebServer.onPath("/cmd", handleCmd)
ESP8266WebServer.onPath("/switch", handleSwitch)
ESP8266WebServer.onPath("/post", handlePost)

# Setting the path to documents
ESP8266WebServer.setDocPath("/")

# Setting data for template
ESP8266WebServer.setTplData(ledData)

# Setting maximum Body Content Size. Set to 0 to disable posting. Default: 1024
ESP8266WebServer.setMaxContentLength(1024)

def checkForClients():
    try:
        while True:
            # Let server process requests
            ESP8266WebServer.handleClient()
    except:
        ESP8266WebServer.close()

checkForClients()

