'''
Used to test circuitry by turning on GPIO pin 24 for 5 seconds
then turning setting pin 24 back to low. 
'''
import RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BCM)

cooler = 24

# Control the LED
GPIO.setup(cooler, GPIO.OUT) # Set Pin as output
GPIO.output(cooler, GPIO.HIGH) # Turn on the LED
time.sleep(5)
GPIO.output(cooler, GPIO.LOW) # Turn off the LED
