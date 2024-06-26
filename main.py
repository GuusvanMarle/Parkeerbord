import network
import time
import socket
import machine
import asyncio
import neopixel
import ujson as json

from ota import OTAUpdater
from WIFI_CONFIG import SSID, PASSWORD

ssid = "Villa BreTil"
password = "Villa5121"

# Check for OTA updates
repo_name = "Parkeerbord"
branch = "main"
firmware_url = f"https://github.com/GuusvanMarle/{repo_name}/{branch}/"

#dagdag

strip = neopixel.NeoPixel(machine.Pin(16), 47)

solarPin = machine.ADC(27)

led = machine.Pin("LED", machine.Pin.OUT)

# white = (45,40,20)
# white1 = (40,36,18)
# white2 = (35,32,16)
# white3 = (30,28,15)
# white4 = (25,22,12)
# white5 = (22,18,10)
# white6 = (20,16,8)
# white7 = (15,12,5)
# white8 = (10,8,3)

white = (85,40,20)
white1 = (80,36,18)
white2 = (75,32,16)
white3 = (60,28,15)
white4 = (55,22,12)
white5 = (42,18,10)
white6 = (30,16,8)
white7 = (25,12,5)
white8 = (15,8,3)


off = (0,0,0)

showState = 0
solarVoltage = 0

solarShow = 0
solarOn = 0
solarOff = 0

apActive = False

mydata = {
            'solarShow': 0,
            'solarOn': 0,
            'solarOff': 0
          }

def index():
  html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Parkeerbord Villa BreTil</title>
    <style type="text/css">
        .body {
            font-family: Arial;
            background-color: #848182;
            text-align: center;
        }

        ul {
          list-style-type: none;
          margin: 20px;
          margin-top: 40px;
          padding: 0;
          overflow: hidden;
          background-color: #333;
        }

        li {
          float: left;
          border-right:5px solid #bbb;
          border-left:5px solid #bbb;
        }

        li a {
          display: block;
          color: white;
          text-align: center;
          font-size: 75px;
          padding: 30px 50px;
          text-decoration: none;
        }

        li a:hover:not(.active) {
          background-color: #111;
        }

        .active {
          background-color: #04AA6D;
        }
        
        .button {
            background-color: #333;
            text-color: white;
            border: none;
            color: white;
            padding: 25px 32px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 50px;
            //margin: 4px 2px;
            cursor: pointer;
            width: 70%;
            border-radius: 6px;
            margin-top: 30px;
        }
        
        h1 {
            font-size: 55px;
            color: white;
        }
        .border {
            border: solid black 4px;
            border-radius: 10px;
            margin: 60px;
            
        }
    </style>
</head>
<body class="body">
    <ul>
        <li><a class="active" href="index.html">Home</a></li>
        <li><a href="settings.html">Instellingen</a></li>
	</ul> 
	
	<div class="border">
        <p>
        <h1>Parkeerbord Villa BreTil Test</h1>
        
        <div>
            <form action="./show"> 
                    <button class="button" type="submit" name="show" value="0">Pijl Uit</button>
            </form>
            <form action="./show"> 
                    <button class="button" type="submit" name="show" value="1">Pijl Aan</button>
            </form>
            <form action="./show"> 
                    <button class="button" type="submit" name="show" value="2">Looplicht</button>
            </form>
            <form action="./show"> 
                    <button class="button" type="submit" name="show" value="3">Kermis Looplicht</button>
            </form>
        </div>
        </p>
	</div>
</body>
</html>
         """
  return str(html)

def settings():
  html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Parkeerbord Villa BreTil</title>
    <style type="text/css">
        .body {
            font-family: Arial;
            background-color: #848182;
            text-align: center;
        }

        ul {
          list-style-type: none;
          margin: 20px;
          margin-top: 40px;
          padding: 0;
          overflow: hidden;
          background-color: #333;
        }

        li {
          float: left;
          border-right:5px solid #bbb;
          border-left:5px solid #bbb;
        }

        li a {
          display: block;
          color: white;
          text-align: center;
          font-size: 75px;
          padding: 30px 50px;
          text-decoration: none;
        }

        li a:hover:not(.active) {
          background-color: #111;
        }

        .active {
          background-color: #04AA6D;
        }
        
        .button {
            background-color: #333;
            text-color: white;
            border: none;
            color: white;
            padding: 25px 32px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 50px;
            //margin: 4px 2px;
            cursor: pointer;
            width: 70%;
            border-radius: 6px;
            margin-top: 30px;
        }
        
        h1 {
            font-size: 65px;
            color: white;
        }
        .border {
            border: solid black 4px;
            border-radius: 10px;
            margin: 60px;
            
        }
        input {
            background-color: white;
            font-size: 45px;
            width: 40%;
        }
        select {
            background-color: white;
            font-size: 45px;
            width: 40%;
        }
        label {
            font-size: 45px;
        }
    </style>
</head>
<body class="body">
    <ul>
        <li><a href="index.html">Home</a></li>
        <li><a class="active" href="settings.html">Instellingen</a></li>
	</ul> 
	
	<div class="border">
        
        <h1> zonnepaneel waarde: """ + str(solarVoltage) + """</h1>
        
        <form action="./solarSettings" id="solarSettings">
            <label for="solarOn">Aan: </label>
            <input placeholder=" """ + str(solarOn) + """ " type="number" id="solarOn" name="solarOn"><br><br>
            <label for="solarOff">Uit: </label>
            <input placeholder=" """ + str(solarOff) + """ " type="number" id="solarOff" name="solarOff"><br><br>
            <label for="solarShow">Show: </label>
            <select name="solarShow" form="solarSettings">
                <option value="1">Aan</option>
                <option value="2">Looplicht</option>
                <option value="3">Kermis Looplicht</option>
                <option value="4">Audi</option>
            </select>
            
            <br>
            <br>
            
            <input type="submit" value="Submit">
        </form>
        <br>
        <br>
        <br>
        <form action="./ota"> 
                    <button class="button" type="submit">OTA Upload</button>
        </form>
        <br>
        <br>
	</div>
</body>
</html>
         """
  return str(html)




wlan = network.WLAN(network.STA_IF)
def init_wifi(ssid, password):
    
    wlan.disconnect()
#     wlan.active(False)
    wlan.active(True)
    # Connect to your network
    wlan.ifconfig(('192.168.22.125', '255.255.255.0', '192.168.22.251', '8.8.8.8'))
    wlan.connect(ssid, password)
    # Wait for Wi-Fi connection
    connection_timeout = 10
    while connection_timeout > 0:
        print(wlan.status())
        if wlan.status() >= 3:
            break
        connection_timeout -= 1
        print('Waiting for Wi-Fi connection...')
        time.sleep(1)
    # Check if connection is successful
    if wlan.status() != 3:
        print('Failed to connect to Wi-Fi')
        return False
    else:
        print('Connection successful!')
        network_info = wlan.ifconfig()
        print('IP address:', network_info[0])
        return True

async def handle_client(reader, writer):
    global showState
    global solarShow
    global brightness
    global solarOn
    global solarOff
    global apActive

    
    response = index()
    
    print("Client connected")
    request_line = await reader.readline()
    
    # Skip HTTP request headers
    while await reader.readline() != b"\r\n":
        pass
    
    request = str(request_line, 'utf-8').split()[1]
    print('Request:', request)
    requestType = request.partition('?')[0]
    print(requestType)
    # Process the request and update variables
    if request == '/show?show=0':
        showState = 0
        strip.fill(off)
        strip.write()
    elif request == '/show?show=1':
        showState = 1
        strip.fill(white)
        strip.write()
    elif requestType == '/show':
        showRequest = request.partition('=')
        showState = int(showRequest[2])
    elif requestType == '/solarSettings':
        solarRequest = request.partition('=')[2]
        if solarRequest.partition('&')[0] != '':
            solarOn = int(solarRequest.partition('&')[0])            
        if solarRequest.partition('=')[2].partition('&')[0] != '':
            solarOff = int(solarRequest.partition('=')[2].partition('&')[0])
        if solarRequest.partition('=')[2].partition('&')[2].partition('=')[2] != '':
            solarShow = int(solarRequest.partition('=')[2].partition('&')[2].partition('=')[2])
        response = settings()
    elif requestType == '/ota':
        ota_updater = OTAUpdater(firmware_url, "main.py")
        ota_updater.download_and_install_update_if_available()
    elif requestType == '/wifi':
        apActive = False
        if wlan.isconnected() == False:
            if apActive == False:
                if not init_wifi(ssid, password):
                    print('Starting AP mode')
                    ap_mode('Parkeerbord Villa BreTil', 'VillaBreTil5121')
                    apActive = True
    
    mydata = {
            'solarShow': solarShow,
            'solarOn': solarOn,
            'solarOff': solarOff
          }
        
    with open('datafile.json', 'w') as f:
        json.dump(mydata, f)
        
    if requestType == '/settings.html':
        response = settings()
        #if request
    elif requestType == '/index.html':
        response = index()

      
    writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    writer.write(response)
    await writer.drain()
    await writer.wait_closed()
    print('Client Disconnected')

# 

def map_range(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

async def main():
    
    global solarVoltage
    global solarShow
    global solarOn
    global solarOff
    global apActive
    
    if not init_wifi(ssid, password):
        print("not connected")
#         print('Starting AP mode')
#         if apActive == False:
#             ap_mode('Parkeerbord Villa BreTil', 'VillaBreTil5121')
#             apActive = True
     
    with open('datafile.json', 'r') as f:
        variables = json.load(f)
        
    solarShow = variables['solarShow']
    solarOn = variables['solarOn']
    solarOff = variables['solarOff']
    
    server = asyncio.start_server(handle_client, "0.0.0.0", 80)
    
    asyncio.create_task(server)

    prevMillis = 0
    direction = False
    arrowIndex = 0;
    
    
    
    while True:
        await asyncio.sleep(0.001)
        currentMillis = time.time_ns() // 1_000_000
#         print(wlan.isconnected())
        if wlan.isconnected() == False:
            led.off()
            if not init_wifi(ssid, password):
                print("help")
        else:
            led.on()
            
        solarVoltage = solarPin.read_u16()
        
        if solarVoltage < solarOn:
            dark = True
        elif solarVoltage > solarOff:
            dark = False
        
        
        if showState == 2:
            if currentMillis - prevMillis > 20:
                prevMillis = currentMillis
                if direction == False:                    
                    strip[clamp(arrowIndex, 0, 34)] = white8
                    strip[clamp(arrowIndex-1,0,34)] = white7
                    strip[clamp(arrowIndex-2,0,34)] = white6
                    strip[clamp(arrowIndex-3,0,34)] = white5
                    strip[clamp(arrowIndex-4,0,34)] = white4
                    strip[clamp(arrowIndex-5,0,34)] = white3
                    strip[clamp(arrowIndex-6,0,34)] = white2
                    strip[clamp(arrowIndex-7,0,34)] = white1
                    strip[clamp(arrowIndex-8,0,34)] = white

                    if arrowIndex > 29 and arrowIndex < 36:
                        strip[map_range(clamp(arrowIndex, 0, 35), 30, 35, 40, 35)] = white
                        strip[map_range(clamp(arrowIndex, 0, 35), 30, 35, 41, 46)] = white
                    strip.write()
                else:
                    if arrowIndex > 7:
                        strip[arrowIndex-8] = off
                    strip[clamp(arrowIndex-7,0,35)] = white8
                    strip[clamp(arrowIndex-6,0,35)] = white7
                    strip[clamp(arrowIndex-5,0,35)] = white6
                    strip[clamp(arrowIndex-4,0,35)] = white5
                    strip[clamp(arrowIndex-3,0,35)] = white4
                    strip[clamp(arrowIndex-2,0,35)] = white3
                    strip[clamp(arrowIndex-1,0,35)] = white2
                    strip[clamp(arrowIndex, 0, 35)] = white1
                    if arrowIndex > 29:
                        strip[map_range(clamp(arrowIndex, 0, 35), 30, 35, 40, 35)] = off
                        strip[map_range(clamp(arrowIndex, 0, 35), 30, 35, 41, 46)] = off
                    strip.write()
                arrowIndex += 1
                if arrowIndex > 42:
                    arrowIndex = 0
                    direction = not direction
      

loop = asyncio.get_event_loop()
loop.create_task(main())

try:
    loop.run_forever()
except Exception as e:
    print('Error occured: ', e)
except KeyboardInterrupt:
    print('Program Interrupted by the user')


