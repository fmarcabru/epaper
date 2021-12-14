from micropython import const
from utime import sleep_ms
import ustruct
from bmp import BitmapHeader, BitmapHeaderInfo


# Display resolution
EPD_WIDTH = const(200)
EPD_HEIGHT = const(200)
# EPD1IN54B commands
PANEL_SETTING = const(0x00)
POWER_SETTING = const(0x01)
POWER_OFF = const(0x02)
POWER_OFF_SEQUENCE_SETTING = const(0x03)
POWER_ON = const(0x04)
POWER_ON_MEASURE = const(0x05)
BOOSTER_SOFT_START = const(0x06)
DEEP_SLEEP = const(0x07)
DATA_START_TRANSMISSION_1 = const(0x10)
DATA_STOP = const(0x11)
DISPLAY_REFRESH = const(0x12)
DATA_START_TRANSMISSION_2 = const(0x13)
VCOM_LUT = const(0x20)
W2W_LUT = const(0x21)  # White LUT
B2W_LUT = const(0x22)  # Black LUT
W2B_LUT = const(0x23)  # not in datasheet
B2B_LUT = const(0x24)  # not in datasheet
LUT_RED_0 = const(0x25)  # Red VCOM LUT
LUT_RED_1 = const(0x26)  # Red0 LUT
LUT_RED_2 = const(0x27)  # RED1 LUT
PLL_CONTROL = const(0x30)
TEMPERATURE_SENSOR_COMMAND = const(0x40)
TEMPERATURE_SENSOR_CALIBRATION = const(0x41)
TEMPERATURE_SENSOR_WRITE = const(0x42)
TEMPERATURE_SENSOR_READ = const(0x43)
VCOM_AND_DATA_INTERVAL_SETTING = const(0x50)
LOW_POWER_DETECTION = const(0x51)
TCON_SETTING = const(0x60)
TCON_RESOLUTION = const(0x61)
SOURCE_AND_GATE_START_SETTING = const(0x62)
GET_STATUS = const(0x71)
AUTO_MEASURE_VCOM = const(0x80)
VCOM_VALUE = const(0x81)
VCM_DC_SETTING_REGISTER = const(0x82)
PROGRAM_MODE = const(0xA0)
ACTIVE_PROGRAM = const(0xA1)
READ_OTP_DATA = const(0xA2)
# Color or no color
COLORED = const(1)
UNCOLORED = const(0)
# Display orientation
ROTATE_0 = const(0)
ROTATE_90 = const(1)
ROTATE_180 = const(2)
ROTATE_270 = const(3)



DATA = const(1)
COMMAND = const(0)


class EPaperDisplay:
    LUT_VCOM0 = bytearray(b"\x0E\x14\x01\x0A\x06\x04\x0A\x0A\x0F\x03\x03\x0C\x06\x0A\x00")
    LUT_W = bytearray(b"\x0E\x14\x01\x0A\x46\x04\x8A\x4A\x0F\x83\x43\x0C\x86\x0A\x04")
    LUT_B = bytearray(b"\x0E\x14\x01\x8A\x06\x04\x8A\x4A\x0F\x83\x43\x0C\x06\x4A\x04")
    LUT_G1 = bytearray(b"\x8E\x94\x01\x8A\x06\x04\x8A\x4A\x0F\x83\x43\x0C\x06\x0A\x04")
    LUT_G2 = LUT_G1
    LUT_VCOM1 = bytearray(b"\x03\x1D\x01\x01\x08\x23\x37\x37\x01\x00\x00\x00\x00\x00\x00")
    LUT_RED0 = bytearray(b"\x83\x5D\x01\x81\x48\x23\x77\x77\x01\x00\x00\x00\x00\x00\x00")
    LUT_RED1 = LUT_VCOM1

    def __init__(self, reset, dc, busy, cs, spi):
        self.reset_pin = reset
        self.dataorcommand_pin = dc
        self.busy_pin = busy
        self.chipselect_pin = cs
        self.spi = spi
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        self.rotate = ROTATE_0
        self.area = self.width * self.height // 8

    def send_data(self, data: bytearray) -> None:
        '''Sends data over SPI'''
        self.dataorcommand_pin(DATA)
        self.chipselect_pin(0)
        self.spi.write(data)
        self.chipselect_pin(1)

    def send_command(self, command: bytes, data: bytearray=None) -> None:
        '''Sends commands over SPI'''
        self.dataorcommand_pin(COMMAND)
        self.chipselect_pin(0)
        self.spi.write(bytearray([command]))
        self.chipselect_pin(1)
        if data:
            self.send_data(data)

    def wait_until_idle(self) -> None:
        """Sleeps until busy pin is on (idle)"""
        while not self.busy_pin():
            sleep_ms(100)

    def sleep(self) -> None:
        """Puts the display to sleep"""
        # to wake call reset() or init()
        self.send_command(VCOM_AND_DATA_INTERVAL_SETTING, data=b"\x17")  # for this panel, must be 0x17
        self.send_command(VCM_DC_SETTING_REGISTER, data=b"\x00")  # to solve Vcom drop
        self.send_command(POWER_SETTING, data=b"\x02\x00\x00\x00")  # gate switch to external
        self.wait_until_idle()
        self.send_command(POWER_OFF)


    def clear(self) -> None:
        '''Clears the display'''
        self.send_command(DATA_START_TRANSMISSION_1)
        for _ in range(self.area):
            self.send_data(b"\xFF\xFF")
        self.send_command(DATA_START_TRANSMISSION_2)
        for _ in range(self.area):
            self.send_data(b"\xFF")
        self.send_command(DISPLAY_REFRESH)
        self.wait_until_idle()

    def setframe(self) -> bytearray:
        '''Creates canvas'''
        return bytearray([0xFF] * self.area)

    def setdarkframe(self) -> bytearray:
        '''Creates dark canvas'''
        return bytearray([0x00] * self.area)

    def reset(self) -> None:
        '''Module reset'''
        self.reset_pin(0)  
        sleep_ms(200)
        self.reset_pin(1)
        sleep_ms(200)

    def set_lut_bw(self) -> None:
        self.send_command(VCOM_LUT, self.LUT_VCOM0)  # vcom
        self.send_command(W2W_LUT, self.LUT_W)  # ww --
        self.send_command(B2W_LUT, self.LUT_B)  # bw r
        self.send_command(W2B_LUT, self.LUT_G1)  # wb w
        self.send_command(B2B_LUT, self.LUT_G2)  # bb b

    def set_lut_red(self) -> None:
        self.send_command(LUT_RED_0, self.LUT_VCOM1)
        self.send_command(LUT_RED_1, self.LUT_RED0)
        self.send_command(LUT_RED_2, self.LUT_RED1)

    def display_frame(self, frame_buffer_black: bytearray, frame_buffer_red: bytearray) -> None:
        '''Shows buffer in display'''
        if frame_buffer_black:
            self.send_command(DATA_START_TRANSMISSION_1)
            sleep_ms(2)
            for pixel in range(self.area):
                temp = 0x00
                for bit in range(4):
                    if frame_buffer_black[pixel] & (0x80 >> bit) != 0:
                        temp |= 0xC0 >> (bit * 2)
                self.send_data(bytearray([temp]))
                temp = 0x00
                for bit in range(4, 8):
                    if frame_buffer_black[pixel] & (0x80 >> bit) != 0:
                        temp |= 0xC0 >> ((bit - 4) * 2)
                self.send_data(bytearray([temp]))
            sleep_ms(2)
        if frame_buffer_red:
            self.send_command(DATA_START_TRANSMISSION_2)
            sleep_ms(2)
            for pixel in range(self.area):
                self.send_data(bytearray([frame_buffer_red[pixel]]))
            sleep_ms(2)

        self.send_command(DISPLAY_REFRESH)
        self.wait_until_idle()


    def init(self) -> None:
        '''Sequence to initialise the display'''
        self.reset()
        self.send_command(POWER_SETTING, b'\x07\x00\x08\x00')
        self.send_command(BOOSTER_SOFT_START, b'\x07\x07\x07')
        self.send_command(POWER_ON)
        self.wait_until_idle()
        self.send_command(PANEL_SETTING, b'\xCF')
        self.send_command(VCOM_AND_DATA_INTERVAL_SETTING, b'\x17') # for this panel, must be 0x17
        self.send_command(PLL_CONTROL, b'\x39') 
        self.send_command(TCON_RESOLUTION, ustruct.pack(">BH", EPD_WIDTH, EPD_HEIGHT)) #b'\xc8\x00\xc8
        self.send_command(VCM_DC_SETTING_REGISTER, b'\x0E') # -1.4V
        self.set_lut_bw()
        self.set_lut_red()

  
    def draw_bmp(self, frame_buffer: bytearray, image_path: str, colored: int) -> None: 
        '''Draws image from pos 0,0'''
        self.draw_bmp_at(frame_buffer, 0, 0, image_path, colored)


    def draw_bmp_at(self, frame_buffer: bytearray, x: int, y: int, image_path: str, colored: int) -> None:
        '''Draws image'''
        if x >= self.width or y >= self.height:
            print("Can't draw here")
            return
        try:
            with open(image_path, 'rb') as bmp_file:
                print("Image found")
                header = BitmapHeader(bmp_file.read(BitmapHeader.SIZE_IN_BYTES))
                header_info = BitmapHeaderInfo(bmp_file.read(BitmapHeaderInfo.SIZE_IN_BYTES))
                if header_info.width > self.width:
                    #print("width of image is bigger than the display")
                    widthClipped = self.width
                elif x < 0:
                    #print("width of the image is smaller than the display")
                    widthClipped = header_info.width + x
                else:
                    #print("width of the image is just right")
                    widthClipped = header_info.width

                if header_info.height > self.height:
                    #print("height of image is bigger than the display")
                    heightClipped = self.height
                elif y < 0:
                    #print("height of the image is smaller than the display")
                    heightClipped = header_info.height + y
                else:
                    #print("height of the image is just right")
                    heightClipped = header_info.height

                heightClipped = max(0, min(self.height-y, heightClipped))
                y_offset = max(0, -y)

                if heightClipped <= 0 or widthClipped <= 0:
                    print("image is broken")
                    return

                width_in_bytes = int(self.width/8)
                if header_info.width_in_bytes > width_in_bytes:
                    rowBytesClipped = width_in_bytes
                else:
                    rowBytesClipped = header_info.width_in_bytes

                for row in range(y_offset, heightClipped):
                    absolute_row = row + y
                    #print("absolute_row {} row {} y {}".format(absolute_row,row,y))
                    # seek to beginning of line
                #    print("data end {}, row {}, line_width {}, seek {}".format(data_end,row,header_info.line_width, data_end - (row + 1) * header_info.line_width))
                    bmp_file.seek(header.file_size - (row + 1) * header_info.line_width)
                #    bmp_file.seek(data_end - (row + 1) * 25)
                #    print("rowbytesclipped {}".format(rowBytesClipped))
                    line = bytearray(bmp_file.read(rowBytesClipped))

                    if header_info.last_byte_padding > 0:
                        mask = 0xFF<<header_info.last_byte_padding & 0xFF
                        line[-1] &= mask

                    for byte_index in range(len(line)):
                        byte = ~line[byte_index]
                        for i in range(8):
                            if byte & (0x80 >> i):
                                self.set_pixel(frame_buffer, byte_index*8 + i + x, absolute_row, colored)

        except OSError as e:
            print("not found")
            print('error: {}'.format(e))

    def set_pixel(self, frame_buffer: bytearray, x: int, y: int, colored: int) -> None:
        if (x < 0 or x >= self.width or y < 0 or y >= self.height):
            #print("Pixel broken")
            return
        if (self.rotate == ROTATE_90):
            point_temp = x
            x = EPD_WIDTH - y
            y = point_temp
        elif (self.rotate == ROTATE_180):
            x = EPD_WIDTH - x
            y = EPD_HEIGHT- y
        elif (self.rotate == ROTATE_270):
            point_temp = x
            x = y
            y = EPD_HEIGHT - point_temp
        self.set_absolute_pixel(frame_buffer, x, y, colored)


    def set_absolute_pixel(self, frame_buffer: bytearray, x: int, y: int, colored: int) -> None:
        # To avoid display orientation effects
        # use EPD_WIDTH instead of self.width
        # use EPD_HEIGHT instead of self.height
        if (x < 0 or x >= EPD_WIDTH or y < 0 or y >= EPD_HEIGHT):
            return
        if colored:
            frame_buffer[int((x + y * EPD_WIDTH) / 8)] &= ~(0x80 >> (x % 8))
        else:
            frame_buffer[int((x + y * EPD_WIDTH) / 8)] |= 0x80 >> (x % 8)
    

    def draw_line(self, frame_buffer: bytearray, x0: int, y0: int, x1: int, y1: int, colored: int) -> None:
        # Bresenham algorithm
        dx = abs(x1 - x0)
        sx = 1 if x0 < x1 else -1
        dy = -abs(y1 - y0)
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while((x0 != x1) and (y0 != y1)):
            self.set_pixel(frame_buffer, x0, y0 , colored)
            if (2 * err >= dy):
                err += dy
                x0 += sx
            if (2 * err <= dx):
                err += dx
                y0 += sy


    def draw_horizontal_line(self, frame_buffer: bytearray, x: int, y: int, width: int, colored: int) -> None:
        for i in range(x, x + width):
            self.set_pixel(frame_buffer, i, y, colored)


    def draw_vertical_line(self, frame_buffer: bytearray, x: int, y: int, height: int, colored: int) -> None:
        for i in range(y, y + height):
            self.set_pixel(frame_buffer, x, i, colored)


    def draw_rectangle(self, frame_buffer: bytearray, x0: int, y0: int, x1: int, y1: int, colored: int) -> None:
        min_x = x0 if x1 > x0 else x1
        max_x = x1 if x1 > x0 else x0
        min_y = y0 if y1 > y0 else y1
        max_y = y1 if y1 > y0 else y0
        self.draw_horizontal_line(frame_buffer, min_x, min_y, max_x - min_x + 1, colored)
        self.draw_horizontal_line(frame_buffer, min_x, max_y, max_x - min_x + 1, colored)
        self.draw_vertical_line(frame_buffer, min_x, min_y, max_y - min_y + 1, colored)
        self.draw_vertical_line(frame_buffer, max_x, min_y, max_y - min_y + 1, colored)


    def draw_filled_rectangle(self, frame_buffer: bytearray, x0: int, y0: int, x1: int, y1: int, colored: int) -> None:
        min_x = x0 if x1 > x0 else x1
        max_x = x1 if x1 > x0 else x0
        min_y = y0 if y1 > y0 else y1
        max_y = y1 if y1 > y0 else y0
        for i in range(min_x, max_x + 1):
            self.draw_vertical_line(frame_buffer, i, min_y, max_y - min_y + 1, colored)


    def draw_circle(self, frame_buffer: bytearray, x: int, y: int, radius: int, colored: int) -> None:
        # Bresenham algorithm
        x_pos = -radius
        y_pos = 0
        err = 2 - 2 * radius
        if (x >= self.width or y >= self.height):
            print("Out of range")
            return
        while True:
            self.set_pixel(frame_buffer, x - x_pos, y + y_pos, colored)
            self.set_pixel(frame_buffer, x + x_pos, y + y_pos, colored)
            self.set_pixel(frame_buffer, x + x_pos, y - y_pos, colored)
            self.set_pixel(frame_buffer, x - x_pos, y - y_pos, colored)
            e2 = err
            if (e2 <= y_pos):
                y_pos += 1
                err += y_pos * 2 + 1
                if(-x_pos == y_pos and e2 <= x_pos):
                    e2 = 0
            if (e2 > x_pos):
                x_pos += 1
                err += x_pos * 2 + 1
            if x_pos > 0:
                break


    def draw_filled_circle(self, frame_buffer: bytearray, x: int, y: int, radius: int, colored: int):
        # Bresenham algorithm
        x_pos = -radius
        y_pos = 0
        err = 2 - 2 * radius
        if (x >= self.width or y >= self.height):
            print("Out of range")
            return
        while True:
            self.set_pixel(frame_buffer, x - x_pos, y + y_pos, colored)
            self.set_pixel(frame_buffer, x + x_pos, y + y_pos, colored)
            self.set_pixel(frame_buffer, x + x_pos, y - y_pos, colored)
            self.set_pixel(frame_buffer, x - x_pos, y - y_pos, colored)
            self.draw_horizontal_line(frame_buffer, x + x_pos, y + y_pos, 2 * (-x_pos) + 1, colored)
            self.draw_horizontal_line(frame_buffer, x + x_pos, y - y_pos, 2 * (-x_pos) + 1, colored)
            e2 = err
            if (e2 <= y_pos):
                y_pos += 1
                err += y_pos * 2 + 1
                if(-x_pos == y_pos and e2 <= x_pos):
                    e2 = 0
            if (e2 > x_pos):
                x_pos  += 1
                err += x_pos * 2 + 1
            if x_pos > 0:
                break

    def draw_char_at(self, frame_buffer: bytearray, x: int, y: int, char: str, font: bytes, colored: int) -> None:
        char_offset = (ord(char) - ord(' ')) * font.height * (int(font.width / 8) + (1 if font.width % 8 else 0))
        offset = 0

        for j in range(font.height):
            for i in range(font.width):
                if font.data[char_offset+offset] & (0x80 >> (i % 8)):
                    self.set_pixel(frame_buffer, x + i, y + j, colored)
                if i % 8 == 7:
                    offset += 1
            if font.width % 8 != 0:
                offset += 1


    def display_string_at(self, frame_buffer: bytearray, x: int, y: int, text: str, font: bytes, colored: int) -> None:
        refcolumn = x

        # Send the string character by character on EPD
        for index in range(len(text)):
            # Display one character on EPD
            self.draw_char_at(frame_buffer, refcolumn, y, text[index], font, colored)
            # Decrement the column position by 16
            refcolumn += font.width


    def draw_char(self, frame_buffer: bytearray, xstart: int, ystart: int, height: int, width: int, glyph: memoryview, colored: int) -> None:
        #char_offset = (ord(char) - ord(' ')) * font.height * (int(font.width / 8) + (1 if font.width % 8 else 0))
        offset = 0

#        chardata=bytes(glyph)
        print("calc {}".format(height*width))
        print("len {}".format(len(glyph)*8))

                
        for x in range(width):
            for y in range(height):
                if glyph[offset] & (0x80 >> (x % 8)):
                    self.set_pixel(frame_buffer, xstart + x, ystart + y, colored)
                if x % 8 == 7:
                    offset += 1
            if height % 8 != 0:
                offset += 1

#        for j in range(height):
#            for i in range(width):
#                if chardata[offset] & (0x80 >> (i % 8)):
#                    self.set_pixel(frame_buffer, x + i, y + j, colored)
#                if i % 8 == 7:
#                    offset += 1
#            if width % 8 != 0:
#                offset += 1


    def display_string(self, frame_buffer: bytearray, x: int, y: int, text: str, font: bytes, colored: int) -> None:
        refcolumn = x
        # Send the string character by character on EPD
        for letter in text:
            #Get char info
            glyph, height, width=font.get_ch(letter)
            # Display one character on EPD
            self.draw_char(frame_buffer, refcolumn, y, height, width, glyph, colored)
            # Decrement the column position by 16
            refcolumn += width


    def draw_ch(self, frame_buffer: bytearray, xstart: int, ystart: int, height: int, width: int, glyph: memoryview, colored: int) -> None:
        #char_offset = (ord(char) - ord(' ')) * font.height * (int(font.width / 8) + (1 if font.width % 8 else 0))
        offset=0
        for x in range(width):
            for y in range(height):
                if glyph[offset] & (0x1 << (y % 8)): # 0x80 = 10000000
                    self.set_pixel(frame_buffer, xstart + x, ystart + y, colored)
                if y % 8 ==7:
                    offset += 1
            if width % 8 !=0:
                offset += 1


    def display_str(self, frame_buffer: bytearray, x: int, y: int, text: str, font: bytes, colored: int) -> None:
        refcolumn = x
        # Send the string character by character on EPD
        for letter in text:
            #Get char info
            glyph, height, width=font.get_ch(letter)
            # Display one character on EPD
            self.draw_ch(frame_buffer, refcolumn, y, height, width, glyph, colored)
            # Decrement the column position by 16
            refcolumn += width


