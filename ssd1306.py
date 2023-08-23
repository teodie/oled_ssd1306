from smbus2 import SMBus, i2c_msg

port = 1         # i2c port beind used
SA = 0x3C # Change this if 0x3D is used instead

"""Fundamental Command"""
SET_CONTRAST_CONTROL = 0x81
ENTIRE_DISPLAY_ON = 0xA4                 # 0xA5 
SET_NORMAL/INVERSE_DISPLAY = 0xA6        # 0xA7
SET_DISPLAY_ON_OFF = 0xAF                # 0xAE

"""Addressing Setting Command"""
SET_MEMORY_ADDRESSING_MODE = 0x20        # A(0x00 ~ 0x02) HORIZONTAL | VERTICAL | PAGE ADDRESSING MODE 

"""Page Addressing Mode 0x02"""
SET_LOWER_COLUMN_START_ADDRESS = 0x00    # 0x00 ~ 0x0F
SET_UPPER_COLUMN_START_ADDRESS = 0x10    # 0x10 ~ 0x1F
SET_PAGE_ADDRESS_PAGE_MODE = 0xB0        # PAGE 0xB0 ~ 0xB7 | PAGE 0 ~ PAGE 7


"""Horizontal/Vertical Addressing Mode"""
SET_COLUMN_ADDRESS = 0x21                # START ADDRESS  A(0x00 ~ 0xFF) | END B(0x00 ~ 0xFF)
SET_PAGE_ADDRESS_VH_MODE = 0x22          # START ADDRESS  A(0x00 ~ 0x07) | END B(0x00 ~ 0x07) END EQUAL OR GREATERTHAN START


"""Hardware Configuratitons"""
SET_DISPLAY_START_LINE = 0x40            # 0x40 ~ 0x7F | RAM DISPLAY LINE REGISTER FROM 0-63 
SET_SEGMENT_RE-MAP = 0xA0                # 0xA0/0xA1 | COLUMN ADDRESS 0 = SEG 0 / COLUMN ADDRESS 127 = SEG 0
SET_MULTIPLEX_RATIO = 0xA8               # A(15d-63d) SET MUX RATIO N+1 MUX FROM 16 MUX TO 64 MUX
SET_COM_OUTPUT_SCAN = 0x0C               # 0x0C/0x08 | NORMAL FROM COM0 TO COM[N-1]/ REMAP COM[N-1] TO COM0 | N is the Multiplex ratio
SET_DISPLAY_OFF_SET = 0xD3               # A(0d ~ 63d) | VERTICAL SHIFT BY COM 0d-63d
SET_COM_PINS = 0xDA                      # A(0x02 ~ 0x32) | REFER TO THE DATASHEET

"""Timing and Driving Scheme Setting"""
SET_DISPLAY_CLOCK = 0xD5                 # A(0x00 ~ 0xFF) REFER TO THE DATASHEET
SET_PRE_CHARGE_PERIOD = 0xD9             # A(0x00 ~ 0xFF) REFER TO THE DATASHEET
SET_VCOM_DESELECT_LEVEL = 0xDB           # A(0x00h ~ 0x30h)
NOP = 0xE3                               # NO OPERATION

def display_initialization():
    pass

def send_command(cmd):
    command =  [0x00] + cmd # insert the low bit for driver command interprita.
    assert (len(command) <= 3), f"Maximu allowed byte is 32 and you have sent {len(command)}"
    print(command)
    #with SMBus(port) as bus:
    #    msg = i2c_msg.write(SA, cmd)

def send_data():
    pass

send_command(test)
