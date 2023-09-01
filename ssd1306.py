from smbus2 import SMBus, i2c_msg
from ascii import ascii
from time import sleep
import random

port = 1         # i2c port beind used
SA = 0x3C # Change this if 0x3D is used instead

"""Fundamental Command"""
SET_CONTRAST_CONTROL = 0x81
ENTIRE_DISPLAY_ON = 0xA4                 # 0xA5 
SET_NORMAL_INVERSE_DISPLAY = 0xA6        # 0xA7
SET_DISPLAY_ON = 0xAF
SET_DISPLAY_OFF = 0xAE

"""Addressing Setting Command"""
SET_MEMORY_ADDRESSING_MODE = 0x20        # A(0x00 ~ 0x02) HORIZONTAL | VERTICAL | PAGE ADDRESSING MODE 
HORIZONTAL = 0x00
VERTICAL = 0x01
PAGE = 0x02

"""Page Addressing Mode 0x02"""
SET_LOWER_COLUMN_START_ADDRESS = 0x00    # 0x00 ~ 0x0F
SET_UPPER_COLUMN_START_ADDRESS = 0x10    # 0x10 ~ 0x1F
SET_PAGE_ADDRESS_PAGE_MODE = 0xB0        # PAGE 0xB0 ~ 0xB7 | PAGE 0 ~ PAGE 7


"""Horizontal/Vertical Addressing Mode"""
SET_COLUMN_ADDRESS = 0x21                # START ADDRESS  A(0x00 ~ 0xFF) | END B(0x00 ~ 0xFF)
SET_PAGE_ADDRESS_VH_MODE = 0x22          # START ADDRESS  A(0x00 ~ 0x07) | END B(0x00 ~ 0x07) END EQUAL OR GREATERTHAN START


"""Hardware Configuratitons"""
SET_DISPLAY_START_LINE = 0x40            # 0x40 ~ 0x7F | RAM DISPLAY LINE REGISTER FROM 0-63 
SET_SEGMENT_RE_MAP = 0xA0                # 0xA0/0xA1 | COLUMN ADDRESS 0 = SEG 0 / COLUMN ADDRESS 127 = SEG 0
SET_MULTIPLEX_RATIO = 0xA8               # A(15d-63d) SET MUX RATIO N+1 MUX FROM 16 MUX TO 64 MUX
SET_COM_OUTPUT_SCAN = 0xC0               # 0x0C/0x08 | NORMAL FROM COM0 TO COM[N-1]/ REMAP COM[N-1] TO COM0 | N is the Multiplex ratio
SET_DISPLAY_OFF_SET = 0xD3               # A(0d ~ 63d) | VERTICAL SHIFT BY COM 0d-63d
SET_COM_PINS = 0xDA                      # A(0x02 ~ 0x32) | REFER TO THE DATASHEET

"""Timing and Driving Scheme Setting"""
SET_DISPLAY_CLOCK = 0xD5                 # A(0x00 ~ 0xFF) REFER TO THE DATASHEET
SET_PRE_CHARGE_PERIOD = 0xD9             # A(0x00 ~ 0xFF) REFER TO THE DATASHEET
SET_VCOM_DESELECT_LEVEL = 0xDB           # A(0x00h ~ 0x30h)
NOP = 0xE3                               # NO OPERATION
ENABLE_CHARGE_PUMP = 0x8D

"""Deactivate Scroll"""
DEACTIVATE_SCROLL = 0x2E

SSD1306_COLUMNS = 128
SSD1306_ROWS = 64
""" Vram to not overide prev drawing """
VRAM = [[0] * SSD1306_COLUMNS for _ in range(SSD1306_ROWS // 8)]


def Initialize_Display():
    send_command(
        SET_DISPLAY_OFF,
        SET_DISPLAY_CLOCK, 0x80,
        SET_MULTIPLEX_RATIO, 0x3F,
        SET_DISPLAY_OFF_SET, 0x00,           # -----------------
        SET_DISPLAY_START_LINE,              # -----------------
        ENABLE_CHARGE_PUMP, 0x14,
        SET_MEMORY_ADDRESSING_MODE, HORIZONTAL,    # ----------------- Set addressing mode
        (SET_SEGMENT_RE_MAP | 0x01),         # ----------------- 0xA1 normal no remap
        (SET_COM_OUTPUT_SCAN | 0x08),        # ----------------- Set to 0xC8
        SET_COM_PINS, 0x12,                  # ----------------- may be critical
        SET_CONTRAST_CONTROL, 0xCF,
        SET_PRE_CHARGE_PERIOD, 0xF1,
        SET_VCOM_DESELECT_LEVEL, 0x40,
        DEACTIVATE_SCROLL,                   # ----------------- Deactivate Scroll 
        ENTIRE_DISPLAY_ON,
        SET_NORMAL_INVERSE_DISPLAY,
        SET_DISPLAY_ON
        )




def send_command(*cmd):
    assert len(cmd) <= 32, f"max allowed is 32 byte you send {len(cmd)}"
    with SMBus(port) as bus:
        bus.write_i2c_block_data(SA, 0x00, list(cmd))


def send_data(data):
    max_chunk_size = 30         # can be 32bytes but error prone so set lower to be safe
    for i in range(0, len(data), max_chunk_size):
        chunk = data[i:i + max_chunk_size]
        
        with SMBus(port) as bus:
            bus.write_i2c_block_data(SA, 0x40, chunk)


def clear_display():
    for page in range(8):
        # tell the start point
        send_command(
            0xB0 + page,      
            0x00,             # set the lower column address
            0x10)             # set the higher column address
        # this line will display 0 to all column in the page
        send_data([0x00] * 128)


# Function to display text at a specific position
def display_p(text, page, column):
    send_command(0xB0 + page,                                   # Set current page
                 column & 0x0F,                                 # Set lower column address
                 ((column & 0xF0) >> 4) | 0x10 )                # Set higher column address
    
    for char in text:

        send_data([0x00]) # blank column before the letter

        char_code = ord(char) - 32  # Adjust the character code to the font data
        for byte in range(5):
            send_data([ascii.FONT[char_code * 5 + byte]])

        send_data([0x00]) # blank column after the letter
        
        print(char, " has been sent")

def display_h(x, y, value):
    assert x <= 128 , "x value can't be higher on 128"
    assert y <= 64, "y value can't be higher than 64"

    page = y >> 3
    #print(page)
    send_command(
            SET_COLUMN_ADDRESS, x, x,
            SET_PAGE_ADDRESS_VH_MODE, page, page)
    #print(hex(value << ( y & 0x07) ))
    if value:
        VRAM[page][x] |= 0x01 << (y & 0x07)
    else:
        VRAM[page][x] &= ~(0x01 << (y & 0x07))
    
    print([VRAM[page][x]])
    send_data([VRAM[page][x]])
    #send_data([value << (y & 0x07)])

def horizontal_scroll(start_page, end_page, frame = 0x00, lr=True):
    direction = 0x26
    if not lr:
        direction = 0x27
    
    #             off, hor,       dum,     start,   frame,   end,    dum ,  dum , activate 
    send_command(0x2E, direction, 0x00, start_page, frame, end_page, 0x00,  0xFF,   0x2F)


Initialize_Display()
#Init_one()
clear_display()

display_h(64,32,1)

#for x in range(128):
#    for y in range(64):
#        display_h(x,y,random.randint(0,1))

#sleep(1)

#for y in range(64):
#    for x in range(128):
#        display_h(x,y,1)

#display_h(10,20,1)
#send_command(0xB0, 0x00, 0x14)
#send_data([0xAA]*12)


#display_text("123456789012345678", 0, 0)
#display_text("HELLO WORLD!!", 0, 20)
#display_text("FIXED", 2, 30)
#horizontal_scroll(0, 0, lr=False)
print("turning off")
