from machine import Pin, SPI
import network, esp

# Garbage collector
import gc

esp.osdebug(0)

gc.collect()

ssid = ""
password = ""

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
    pass

print("Connection successful")
print(station.ifconfig())


#BUSY TO GPIO25
##RST TO GPIO26 (RESET)
###DC TO GPIO27
###CS TO GPIO15 (CHIP SELECT)
##CLK TO GPIO14 (CLOCK)
##DIN TO GPIO13 (MOSI)
#GND
#VCC 3.3V
   
busy = Pin(25, Pin.IN)
rst = Pin(26, Pin.OUT)
dc = Pin(27, Pin.OUT)
cs = Pin(15, Pin.OUT)
clk = Pin(14)
mosi = Pin(13)

#example in https://docs.micropython.org/en/latest/esp32/quickref.html#hardware-spi-bus 
spi = SPI(1, baudrate=2000000, polarity=0, sck=clk, mosi=mosi)


