import driver
import uping
from utime import sleep_ms
from micropython import mem_info
import usys as sys

import firasansbold25capsnum as example_font



def display_image(epaper: driver.EPaperDisplay, image: str, frame: str)-> None:
    epaper.draw_bmp('black',"frame2.bmp",driver.COLORED)


def prepare_display(rst: Pin, dc: Pin, busy: Pin, cs: Pin, spi: SPI):
    print(spi)
    epaper = driver.EPaperDisplay(rst, dc, busy, cs, spi)
    epaper.rotate=driver.ROTATE_270
    epaper.init()
    epaper.clear()
    epaper.sleep()
    return (epaper)



def send_to_display(display: driver.EPaperDisplay):
    print("init display")
    display.init()
    print("clearing display")
    display.clear()
    print("printing frame")
    display.display_frame()
    print("sleeping")
    display.sleep()

try:
    #mem_info(True)
    epaper = prepare_display(rst, dc, busy, cs, spi)

    while True:
        #show bmp 
        epaper.draw_bmp('black',"black_test.bmp",driver.COLORED)
        epaper.draw_bmp('red', 'red_test.bmp', driver.COLORED)
        send_to_display(epaper)
        sleep_ms(10000)

        #show text
        epaper.clear_canvas('black')
        epaper.clear_canvas('red')
        epaper.display_str("black", 20, 20, "12345", example_font, colored=driver.COLORED)
        epaper.display_str("red",20, 100, "AABBCC", example_font, colored=driver.COLORED)
        send_to_display(epaper)
        sleep_ms(10000)

        #show circle
        epaper.clear_canvas('black')
        epaper.clear_canvas('red')
        epaper.draw_filled_circle('black', 20, 30, 20, driver.COLORED)
        epaper.draw_filled_circle('red', 100, 100, 30, driver.COLORED)
        epaper.draw_circle('black', 100, 100, 50, driver.COLORED)
        epaper.draw_circle('black', 100, 100, 51, driver.COLORED)
        send_to_display(epaper)
        sleep_ms(10000)

        #show rectangle
        epaper.clear_canvas('black')
        epaper.clear_canvas('red')
        epaper.draw_filled_rectangle('black', 10, 10, 90, 90, driver.COLORED)
        epaper.draw_filled_rectangle('red', 110, 110, 190, 190, driver.COLORED)
        epaper.draw_rectangle('black', 5, 5, 195,195, driver.COLORED)
        send_to_display(epaper)


        sleep_ms(10000)

        

    


except Exception as e:
#    mem_info(True)
    print(sys.print_exception(e))
    epaper.init()
    epaper.clear()
    epaper.sleep()

except KeyboardInterrupt:
    print("Interrupt detected")
    epaper.init()
    epaper.clear()
    epaper.sleep()
   
    