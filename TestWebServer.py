import ESP8266WebServer
import network
import machine

GPIO_NUM = 2 # Builtin led

# Wi-Fi configuration
STA_SSID = "YOUR SSID"
STA_PSK = "YOUR PASSWORD"

# HTML content for "/"
rootPage = """\
  <!DOCTYPE html>
  <head>
    <meta charset='UTF-8'>
  </head>
  <title>{0}</title>
  <body>
    {0}Status：<span style='color:{1}'>{2}</span><br>
    <a href='/cmd?led={3}'>{4}</a><br>
    <a href='/'>HOME</a>
  </body>
  </html>
  """

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
print("Server started @ ", sta_if.ifconfig()[0])

# Get pin object for controlling builtin LED
pin = machine.Pin(GPIO_NUM, machine.Pin.OUT)
pin.on() # Turn LED off (it use sinking input)

# Handler for path "/" 
def handleRoot(socket, args):
  global rootPage
  # Replacing title text and display text color according 
  # to the status of LED
  response = rootPage.format(
    "Remote LED", 
    "red" if pin.value() else "green",
    "Off" if pin.value() else "On",
    "on" if pin.value() else "off",
    "Turn on" if pin.value() else "Turn off"
  )
  # Return the HTML page
  ESP8266WebServer.ok(socket, "200", response)

# Handler for path "/cmd?led=[on|off]"    
def handleCmd(socket, args):
  if 'led' in args:
    if args['led'] == 'on':
      pin.off()
    elif args['led'] == 'off':
      pin.on()
    handleRoot(socket, args)
  else:
    ESP8266WebServer.err(socket, "400", "Bad Request")

# handler for path "/switch" 
def handleSwitch(socket, args):
  pin.value(not pin.value()) # Switch back and forth
  ESP8266WebServer.ok(
    socket, 
    "200", 
    "On" if pin.value() == 0 else "Off")

# Start the server @ port 8899
ESP8266WebServer.begin(8899)

# Register handler for each path
ESP8266WebServer.onPath("/", handleRoot)
ESP8266WebServer.onPath("/cmd", handleCmd)
ESP8266WebServer.onPath("/switch", handleSwitch)

# Setting the path to documents
ESP8266WebServer.setDocPath("/www")

while True:
  # Let server process requests
  ESP8266WebServer.handleClient()

