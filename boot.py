from machine import Pin, SPI
import network, esp

# Garbage collector
import gc

esp.osdebug(0)


gc.collect()

ssid = "abcdefg"
password = "Dani1504"

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
    pass

print("Connection successful")
print(station.ifconfig())


"""cs = Pin(5, Pin.OUT)

dc = Pin(25, Pin.OUT)
rst = Pin(26, Pin.OUT)
busy = Pin(27, Pin.OUT)
sck = Pin(18)
mosi = Pin(23)
vspi = SPI(3, baudrate=2000000, polarity=0, phase=0, sck=sck, mosi=mosi, miso=Pin(19))"""


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
#cs = Pin(15)
cs = Pin(15, Pin.OUT)
clk = Pin(14)
mosi = Pin(13)

#example in https://docs.micropython.org/en/latest/esp32/quickref.html#hardware-spi-bus says
# hspi = SPI(1, 10000000, sck=Pin(14), mosi=Pin(13), miso=Pin(12))
spi = SPI(1, baudrate=2000000, polarity=0, sck=clk, mosi=mosi)
#need to initialize the chip select pin.
#cs = Pin(15, Pin.OUT)

