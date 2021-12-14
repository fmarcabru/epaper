import driver
from utime import sleep_ms
# from utime import ticks_ms, ticks_diff
#import OpenSansBold as font
#import OpenSansBoldDigits20 as digits20
import OpenSansBoldDigits20 as digits30
#import OpenSansBoldDigits39 as digits40
#import OpenSansBoldDigits as digits50
#from micropython import mem_info
#import antonio20 as font20


print(spi)
#print("here is the memory {}".format(mem_info(True)))
epaper = driver.EPaperDisplay(rst, dc, busy, cs, spi)
epaper.init()
epaper.clear()
frame_black = epaper.setframe()
print("here")
frame_red = epaper.setframe()
print("Frame set!")
#print("here is the memory {}".format(mem_info(True)))
#start=ticks_ms()
epaper.draw_bmp_at(frame_black,120,10,'icon.bmp',driver.COLORED)
#end=ticks_ms()
#epaper.draw_filled_circle(frame_red, 10, 10, 25, driver.COLORED)
#print("Load image time: {}".format(ticks_diff(end,start))) 


xpos=30
ypos=50

#for i in range(1,8):
#    for j in range(-1,2):
#        epaper.draw_vertical_line(frame_black,(xpos+j)*i+font.width,ypos,font.height,driver.COLORED)


#for i in range(3):
#    epaper.draw_horizontal_line(frame_black,xpos,ypos-i,font.width*7,driver.COLORED)

#for i in range(3):
#    epaper.draw_horizontal_line(frame_black,xpos,ypos+i+font.height,font.width*7,driver.COLORED)

#print(type(font))

epaper.display_str(frame_black, 120, ypos, "what is here", digits30, driver.COLORED)
xpos=30
ypos=120
epaper.display_str(frame_black, 10, 90, "1234", digits30, driver.COLORED)
epaper.display_str(frame_black, 10, 10, "1234", digits30, driver.COLORED)
epaper.display_str(frame_black, 10, 40, "1234", digits30, driver.COLORED)
#epaper.display_str(frame_red, 10, 90, "1234", digits40, driver.COLORED)
epaper.display_str(frame_black, 10, 150, "1234", digits30, driver.COLORED)
#epaper.display_string_at(frame_black, 30, 30, "More 45", font, driver.COLORED)


#epaper.draw_vertical_line(frame_black,99,100,font.height,driver.COLORED)
#epaper.draw_vertical_line(frame_black,100,100,font.height,driver.COLORED)
#epaper.draw_vertical_line(frame_black,100+font.width,100,font.height,driver.COLORED)
#epaper.draw_vertical_line(frame_black,101+font.width,100,font.height,driver.COLORED)
#epaper.draw_horizontal_line(frame_black,100,100,font.width,driver.COLORED)
#epaper.draw_horizontal_line(frame_black,100,99,font.width,driver.COLORED)
#epaper.draw_horizontal_line(frame_black,100,100+font.height,font.width,driver.COLORED)
#epaper.draw_horizontal_line(frame_black,100,101+font.height,font.width,driver.COLORED)

#epaper.display_string_at(frame_black, 100, 100, "M", font, driver.COLORED)


epaper.display_frame(frame_black, frame_red)




#print("FONT DATA TYPE {}".format(type(font.data)))
print("finish")
##epaper.sleep() 
sleep_ms(10000)
epaper.init()
epaper.clear()
epaper.sleep() 
print("last")