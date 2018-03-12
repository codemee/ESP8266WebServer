import ESP8266WebServer
import network
import machine

TITLE = "空調"
GPIO_NUM = 2

# 測試用的無線網路
STA_SSID = "FLAG-SCHOOL"
STA_PSK = "12345678"
STA_SSID = "MEE_MI"
STA_PSK = "PinkFloyd1969"

# "/" 路徑要傳回的網頁內容
rootPage = """\
  <!DOCTYPE html>
  <head>
    <meta charset='UTF-8'>
  </head>
  <title>{0}</title>
  <body>
    {0}狀態：<span style='color:{1}'>{2}</span><br>
    <a href='/cmd?led={3}'>{4}</a><br>
    <a href='/'>回首頁</a>
  </body>
  </html>
  """
# End configuration

# 關閉自身的無線 AP
ap_if = network.WLAN(network.AP_IF)
if ap_if.active():
  ap_if.active(False)
  
# 啟用無線網路功能
sta_if = network.WLAN(network.STA_IF)
if not ap_if.active():
  sta_if.active(True)
# 如果沒有連上無線網路, 就連上一開始設定的無線網路
if not sta_if.isconnected():
  sta_if.connect(STA_SSID, STA_PSK)
  while not sta_if.isconnected(): # 等待連上無線網路
    pass

# 顯示自身的 IP 位址
print("伺服器位址 ", sta_if.ifconfig()[0])

# 取得內建 LED 的控制腳位
pin = machine.Pin(GPIO_NUM, machine.Pin.OUT)
pin.on() # 熄掉 LED 燈, 它是 sinking 接法

# 處理 "/" 路徑的函式
def handleRoot(socket, args):
  global rootPage
  response = rootPage.format(
    "空調", # 取代標題文字, 以下依據開關狀態取代網頁上的文字及顏色
    "red" if pin.value() else "green",
    "已關閉" if pin.value() else "已開啟",
    "on" if pin.value() else "off",
    "開啟" if pin.value() else "關閉"
  )
  # 傳回替換過文字的主頁面
  ESP8266WebServer.ok(socket, "200", response)

# 處理 "/cmd?led=[on|off]" 路徑的函式    
def handleCmd(socket, args):
  if 'led' in args:
    if args['led'] == 'on':
      pin.off()
    elif args['led'] == 'off':
      pin.on()
    handleRoot(socket, args)
  else:
    ESP8266WebServer.err(socket, "400", "Bad Request")

# 處理 "/switch" 路徑的函式, 切換 LED 開關
def handleSwitch(socket, args):
  pin.value(not pin.value()) # 切換相反狀態
  ESP8266WebServer.ok(
    socket, 
    "200", 
    "已開啟" if pin.value() == 0 else "已關閉")

# 用 8899 埠號啟用網頁伺服器
ESP8266WebServer.begin(8899)
# 指定個別路徑的處理函式
ESP8266WebServer.onPath("/", handleRoot)
ESP8266WebServer.onPath("/cmd", handleCmd)
ESP8266WebServer.onPath("/switch", handleSwitch)
# 指定網頁伺服器的文件資料夾位置
ESP8266WebServer.setDocPath("/www")

while True:
  # 讓伺服器檢查是否有新的請求並加以處理
  ESP8266WebServer.handleClient()

