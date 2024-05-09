#DIR: 00 - Tail to MOTOR; 01 - MOTOR to Tail (Need to set on-device dir for Camera axis to CCW)
#ID: 01 - Camera (X-Axis)
#    02 - FILM (Z-Axis * 2)
#    03 - Focus (Y_Axis * 2)

#   Function Params assume decimal ints/flaots

import serial

### Motor serial command and flag bits ###
FLAG_CW                 = '00'
FLAG_CCW                = '01'
FLAG_NO_SYNC            = '00'
FLAG_SYNC               = '01'
SYNC                    = 'FF66'
M_ENABLE                = 'F3AB'
CONTROL_VELOCITY_MODE   = 'F6'
CONTROL_POSITION_MODE   = 'FD'
IMMIDIATE_STOP          = 'FE98'

def init(path = "/dev/ttyAMA0", baud = 115200, time_out = 1):
    global ttl 
    ttl = serial.Serial(path, baudrate = baud, timeout = time_out)

def m_enable(address, enable):
    add = hex(address)
    ttl.read(10)

def test():
    console = serial.Serial("/dev/ttyAMA0", baudrate=115200, timeout=1)
    #data = bytes.fromhex('01FD0000FF00000005DC00006B')
    data0 = bytes.fromhex('02FD0000DF0000004D0000006B')
    data1 = bytes.fromhex('029A02006B')
    #data = bytes.fromhex('014CAE010200003F00007530012C0320003C006B')
    console.write(data1)
    line = console.read(10)
    print(line.hex())
    console.close()

if __name__ == '__main__':
    ### PUT TESTS HERE ###
    init()
    test()