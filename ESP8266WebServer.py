# 簡易的網頁伺服器
# 只處理 GET

import network
import machine
import socket
import uselect
import os

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# 查詢是否有新的用戶端連線用
poller = uselect.poll()
# 登記個別路徑的處理函式
handlers = {}
# 網頁文件的資料夾路徑
docPath = "/"

# 啟動伺服器
def begin(port):
  global server
  server.bind(('0.0.0.0', port))
  server.listen(1)
  # 登記要詢問 server 是否有收到新的連線
  poller.register(server, uselect.POLLIN)

# 檢查是否有新的連線, 並加以處理新的請求
def handleClient():
  global server
  res = poller.poll(0)
  if res:  # 表示 server 有新的連線進來
    (socket, sockaddr) = server.accept()
    handle(socket)
    socket.close()

# 回覆錯誤訊息給用戶端
def err(socket, code, message):
  socket.write("HTTP/1.1 " + code + " " + message + "\r\n\r\n")
  socket.write("<h1>" + message + "</h1>")

# 傳回正確的回應給用戶端  
def ok(socket, code, msg):
  socket.write("HTTP/1.1 " + code + " OK\r\n\r\n")
  socket.write(msg)

# 處理新的 GET 請求
def handle(socket):
  global docPath, handlers
  currLine = str(socket.readline(), 'utf-8')
  request = currLine.split(" ")
  if len(request) != 3: # 若表頭第一行格式不對就不處理
    return
  (method, url, version) = request
  if "?" in url: # 如果帶有參數
    (path, query) = url.split("?", 2)
  else:
    (path, query) = (url, "")
  args = {}
  if query: # 解析參數內容
    argPairs = query.split("&")
    for argPair in argPairs:
      arg = argPair.split("=")
      args[arg[0]] = arg[1]
  while True: # 一直讀取到表頭後的空行
    header = socket.readline()
    if header == b"":
      return
    if header == b"\r\n":
      break

  # 檢查 HTTP 版本
  if version != "HTTP/1.0\r\n" and version != "HTTP/1.1\r\n":
    err(socket, "505", "Version Not Supported")
  elif method == "GET": # 本程式庫只處理 GET
    if path.find(docPath) == 0: # 若是取用文件檔
      try:
        os.stat(path) # 檢查檔案是否存在？
        # 送出回應表頭給用戶端
        socket.write("HTTP/1.1 200 OK\r\n\r\n")
        # 送出檔案內容給用戶端
        f = open(path, "rb")
        while True:
          data = f.read(64)
          if (data == b""):
            break
          socket.write(data)
        return
      except: # 找不到名稱相符的檔案
        err(socket, "404", "Not Found")
    elif path in handlers: # 是否為已登記處理函式的路徑
      handlers[path](socket, args)
    else:
      err(socket, "400", "Bad Request")
  else:
    err(socket, "501", "Not Implemented")

# 登記處理指定路徑的函式
def onPath(path, handler):
  global handlers
  handlers[path] = handler

# 設定文件的資料夾位置
def setDocPath(path):
  global docPath
  docPath = path

