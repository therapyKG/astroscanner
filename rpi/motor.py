from gpiozero import PWMOutputDevice, DigitalOutputDevice
import time

stepper_ena = DigitalOutputDevice(4)
stepper = PWMOutputDevice(17, frequency=100)

stepper_ena.on()
time.sleep(0.5)
stepper.on()
time.sleep(3)
stepper.off()