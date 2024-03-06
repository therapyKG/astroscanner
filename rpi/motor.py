import serial
ttl = serial.Serial("/dev/ttyAMA0", baudrate=115200, timeout=1)
data = bytes.fromhex('01FD0100FF00000005DC00006B')
ttl.write(data)
line = ttl.read(10)
print(line.hex())
ttl.close()