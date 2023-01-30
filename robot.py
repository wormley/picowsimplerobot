import network
import picozero
from phew import server
from phew.template import render_template
import uasyncio
import re
numre = re.compile("([-0-9.]+)\s+([-0-9.]+)\s+([-0-9.]+)")
moving=0

picozero.pico_led.on()

m1 = picozero.Motor(0,1)
m2 = picozero.Motor(2,3)
m1.off()
m2.off()


with open("net.txt","r") as f:
    host = f.readline().strip()
    ssid = f.readline().strip()
    password = f.readline().strip()

wlan = network.WLAN(network.STA_IF)
if not wlan.isconnected():
    wlan.active(True)
# Yay, this doesn't yet work, even months later
#    wlan.config(hostname = host)
    wlan.connect(ssid,password)
    while not wlan.isconnected():
        pass
    
own_ip_address = wlan.ifconfig()[0]
picozero.pico_led.off()

code=""



print("Bob "+own_ip_address)

@server.route("/",methods=["GET"])
def root(request):
    return await render_template("root.html",code=code)

@server.route("/post",methods=["POST"])
def post(request):
    global moving
    global code
    code = request.form.get("code","")
    moving = 2
    return await render_template("root.html",code=code)

@server.route("/stop",methods=["GET"])
def stop(request):
    global moving
    m1.off()
    m2.off()
    moving=0
    
    return await render_template("root.html",code=code)

@server.catchall()
def catchall(request):
  return "Not found", 404


async def move():
    global moving
    while True:
        while moving == 0:
            m1.off()
            m2.off()
            picozero.pico_led.on()
            await uasyncio.sleep(0.5)
            picozero.pico_led.off()
            await uasyncio.sleep(0.5)
        movearray = []        
        for l in code.splitlines():
            print(l)
            x= numre.search(l)
            if (x):
                print("Moo")
                movearray.append([float(x.group(1)),
                                float(x.group(2)),
                                float(x.group(3))
                                ])
        moving = 1
        picozero.pico_led.on()
        for i in movearray:
            if (moving != 1 ):
                break
            m1.on(i[0])
            m2.on(i[1])
            await uasyncio.sleep(i[2])
        moving = 0
        m1.off()
        m2.off()


myloop = uasyncio.get_event_loop()
myloop.create_task(move())

server.run()

