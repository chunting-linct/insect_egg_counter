from picamera2 import Picamera2
import RPi.GPIO as GPIO
import time
import io
import os


camera = Picamera2()
camera.start()
camera.set_controls({"AfMode": 2})
time.sleep(1)
step_1 = 20
step_2 = 21
dir_1 = 26
dir_2 = 19
pins = [step_1, step_2, dir_1, dir_2]
GPIO.setmode(GPIO.BCM)
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)

def step(step_pin, dir_pin, steps, direction, delay=0.001):
    GPIO.output(dir_pin, direction)

    for _ in range(steps):
        GPIO.output(step_pin, GPIO.HIGH)
        time.sleep(delay)   # HIGH time
        GPIO.output(step_pin, GPIO.LOW)
        time.sleep(delay)   # LOW time
flag = 1
i = 1000
path = "/home/linct/Pictures/"
for file in os.listdir(path):
    os.remove(os.path.join(path, file))

for x in range(10):
    for y in range(10):
        time.sleep(0.5)
        camera.capture_file(os.path.join(path, f"{i}.jpg"))
        i += 1
        if flag == 1:
            direction = GPIO.HIGH
        else:
            direction = GPIO.LOW
        step(step_2, dir_2, 50, direction)
    time.sleep(0.5)
    camera.capture_file(os.path.join(path, f"{i}.jpg"))
    i += 1
    step(step_1, dir_1, 30, GPIO.HIGH)
    flag *= -1
    
