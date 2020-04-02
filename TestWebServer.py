import ESP8266WebServer
import network
import machine

GPIO_NUM = 2 # Builtin led (D4)

# Wi-Fi configuration
STA_SSID = "SSID"
STA_PSK = "PASSWORD"

# Disable AP interface
ap_if = network.WLAN(network.AP_IF)
if ap_if.active():
    ap_if.active(False)
  
# Connect to Wi-Fi if not connected
sta_if = network.WLAN(network.STA_IF)
if not ap_if.active():
    sta_if.active(True)
if not sta_if.isconnected():
    sta_if.connect(STA_SSID, STA_PSK)
    # Wait for connecting to Wi-Fi
    while not sta_if.isconnected(): 
        pass

# Show IP address
print("Server started @", sta_if.ifconfig()[0])

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
ESP8266WebServer.begin(8899)

# Register handler for each path
# ESP8266WebServer.onPath("/", handleRoot)
ESP8266WebServer.onPath("/cmd", handleCmd)
ESP8266WebServer.onPath("/switch", handleSwitch)

# Setting the path to documents
ESP8266WebServer.setDocPath("/")

# Setting data for template
ESP8266WebServer.setTplData(ledData)

try:
    while True:
        # Let server process requests
        ESP8266WebServer.handleClient()
except:
    ESP8266WebServer.close()
