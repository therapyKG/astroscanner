#DIR: CW - Tail to MOTOR; CCW - MOTOR to Tail (Need to set on-device dir for Camera axis to CCW)
#ID: 01 - Camera (X-Axis)
#    02 - FILM (Z-Axis * 2)
#    03 - Focus (Y_Axis * 2)

#   Function Params assume decimal ints/flaots

import serial

### Global literals
GLOBAL_CHECKSUM         = '6B'
CAMERA_ID               = '01'
FILM_ID                 = '02'
FOCUS_ID                = '03'

GLOBAL_STEPPING         = 16.0
GLOBAL_ANGLE            = 1.8
### Motor serial command and flag bits ###
CW                      = '00'      # CW - Tail to MOTOR
CCW                     = '01'      # CCW - MOTOR to Tail
FLAG_NO_SYNC            = '00'
FLAG_SYNC               = '01'
FLAG_RELATIVE_POSITION  = '00'
FLAG_ABSOLUTE_POSITION  = '01'
SYNC                    = 'FF66'
M_ENABLE                = 'F3AB'
CONTROL_VELOCITY_MODE   = 'F6'
CONTROL_POSITION_MODE   = 'FD'
IMMIDIATE_STOP          = 'FE98'

def init(path = "/dev/ttyAMA0", baud = 115200, time_out = 1):
    global ttl 
    ttl = serial.Serial(path, baudrate = baud, timeout = time_out)

def m_enable(address, enable):
    add = hex(address).lstrip("0x")
    ttl.read(10)

def mm_to_pulse(mm: float, mm_per_rot: int):
    degree = (mm / mm_per_rot ) * 360
    pulse = (degree / GLOBAL_ANGLE) * GLOBAL_STEPPING

    if pulse <= 1: print("ALARM: TRAVEL DISTANCE TOO SHORT")
    return int(pulse)

def move_position_mode(id, direction, velocity, acceleration, num_pulse, sync = False, relative = True, checksum = GLOBAL_CHECKSUM):
    v_str = hex(velocity).lstrip("0x").zfill(4).upper()
    acc_str = hex(acceleration).lstrip("0x").zfill(2).upper()
    pulse_str = hex(num_pulse).lstrip("0x").zfill(8).upper()
    data = id + CONTROL_POSITION_MODE + direction + v_str + acc_str + pulse_str + ('01' if sync else '00') + (FLAG_RELATIVE_POSITION if relative else FLAG_ABSOLUTE_POSITION) + checksum

    ttl.write(bytes.fromhex(data))
    print('move_position_mode sent: ' + data)
    line = ttl.read(10)
    print('move_position_mode received response: ' + line.hex())

#same as move_position mode but takes um as unit of travel instead of number of pulses
def MPM(id, direction, velocity, acceleration, distance, sync = False, relative = True, checksum = GLOBAL_CHECKSUM):
    pulse = mm_to_pulse(distance, 4)
    move_position_mode(id, direction, velocity, acceleration, pulse, sync, relative, checksum)

def z_move(dir):
    if dir == 'up':
        focus_move(CW, 100, 0.01)
        data = bytes.fromhex('03FD0000DF00000000FF00006B')
    elif dir == 'down':
        focus_move(CCW, 100, 0.01)
        data = bytes.fromhex('03FD0100DF00000000FF00006B')


def cam_move(dir, rpm, distance):
    MPM(CAMERA_ID, dir, rpm, 0, distance)

def focus_move(dir, rpm, distance):
    MPM(FOCUS_ID, dir, rpm, 0, distance)

def film_move(dir, rpm, distance):
    MPM(FILM_ID, dir, rpm, 0, distance)

if __name__ == '__main__':
    ### PUT TESTS HERE ###
    init()
    #cam_move(CW, 300, 8)
    focus_move(CW, 100, 10)