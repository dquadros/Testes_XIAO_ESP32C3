# webled - controle de LED via página web gerada pelao XIAO-ESP32C3
# (C) 2023, Daniel Quadros
#
# Baseado em https://sigmdel.ca/michel/ha/xiao/xiao_esp32c3_intro_en.html

from machine import Pin
import network
import socket
import time

# LED conectado a GPIO10 / MOSI
Led = Pin(10, Pin.OUT)

# Indica início execução com uma piscada do LED
Led.on()
time.sleep(1)
Led.off()
time.sleep(1)

ledstatus = 0

# Muda estado do LED
def mudaled():
  global ledstatus
  ledstatus = 1-ledstatus
  Led.value(ledstatus)
  print('LED {}'.format("ligado" if ledstatus else "desligado"))

# Vamos criar uma rede WiFi
rede = "XIAOC3"
ap_if = network.WLAN(network.AP_IF)
ap_if.config(essid=rede, password='123456789', authmode=network.AUTH_WPA_WPA2_PSK)
ap_if.config(max_clients=3)
ap_if.ifconfig(('192.168.0.1', '255.255.255.0', '192.168.0.1', '192.168.0.1'))
ap_if.active(True)
print("Iniciada rede {}".format(rede))

# Aguardar conexões em 192.168.0.1:80
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# avoid [Errno 112] EADDRINUSE on restarting the script quickly
# https://forum.micropython.org/viewtopic.php?t=10412#p57684
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('0.0.0.0', 80))
s.listen(3)
print('Web server iniciado em http://' + ap_if.ifconfig()[0])

# Indica no LED que está ponto para aceitar conexões
for i in range(3):
  for j in range(2):
      Led.on()
      time.sleep_ms(50)
      Led.off()
      time.sleep_ms(50)
  time.sleep_ms(250)

# Envia header de response code 200
def header_ok(conn):
    conn.send ('HTTP/1.1 200 OK\n')

# Envia header de response code 404
def header_notfound(conn):
    conn.send ('HTTP/1.1 404 Not Found\n')

# Envia header de content type
def header_conttype(conn):
    conn.send ('Content-Type: text/html\n')

# Envia header de connection
def header_conn(conn, close):
    conn.send ('Connection: close\n\n' if close else 'Connection: keep-alive\n\n')

# Parte inicial do HTML da resposta
def htmlTop():
  return """<!DOCTYPE html>
      <html>
        <head>
        <title>XIAO ESP32C3 webled</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <link rel="icon" href="data:,">
        <style>
        html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
        h1{color: #0F3376; padding: 2vh;}
        p{font-size: 1.5rem;}
        .button{display: inline-block; background-color: blue; border: none; border-radius: 6px;
        color: white; font-size: 1.5rem; width: 5em; height: 3em; text-decoration: none; margin: 2px; cursor: pointer;}
        .button2{background-color: silver;}
        </style>
        </head>
        <body>
        <h1>XIAO ESP32C3 webled</h1>"""

# Parte final do HTML da resposta
def htmlBottom():
  return "</body></html>"

# Envia pagina de erro 404
def page_404(conn):
    conn.send (htmlTop() + """<h1 style="color: red">Erro 404</h1>
        <p><a href="/"><button class="button button2">Volta</button></a></p>
        """ + htmlBottom())

# Envia página com o estado do LED
def page_led(conn, status):
    conn.send(htmlTop() + """<p>LED: <strong>""" + ("LIGADO" if status else "DESLIGADO") + """</strong></p>
      <p><a href="/?led=toggle"><button class="button">Muda</button></a></p>
      <p><a href="/quit"><button class="button button2">Encerra</button></a></p>
      """ + htmlBottom())

# loop principal
continua = True
while continua:
  # aguarda conexão
  conn, addr = s.accept()
  print()
  print('Conexao de {}'.format(addr))
  
  # le a requisição
  request = conn.recv(1024)
  request = str(request)
  print('Resquest {}...'.format(request[0:31]))
  
  # analisa a requisicao
  erro_404 = False
  if request.find('/quit ') == 6:
    print ("Encerrando")
    continua = False
  elif request.find('/?led=toggle ') == 6:
    mudaled()
  elif request.find('/ ') != 6:
    print ("Erro 404")
    erro_404 = True

  # Envia a resposta
  if erro_404:
    header_notfound(conn)
    header_conttype(conn)
    header_conn(conn, True)
    page_404(conn)
  elif continua:
    header_ok(conn)
    header_conttype(conn)
    header_conn(conn, False)
    page_led(conn, ledstatus)
  else:
    header_ok(conn)
  conn.close()
