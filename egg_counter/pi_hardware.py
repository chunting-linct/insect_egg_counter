import time
import numpy as np
try:

    from picamera2 import Picamera2
    import RPi.GPIO as GPIO
except ImportError:

    class MockGPIO:
        BCM = "BCM"
        OUT = "OUT"
        HIGH = 1
        LOW = 0

        def setmode(self, *args): print("[MOCK] setmode", args)
        def setup(self, *args): print("[MOCK] setup", args)
        def output(self, *args): print("[MOCK] output", args)
        def cleanup(self): print("[MOCK] cleanup")

    GPIO = MockGPIO()
    class MockCamera:
        def capture_array(self):
            # Return dummy image or use OpenCV to generate a blank frame
            return np.zeros((480, 640, 3), dtype=np.uint8)
        def start(self, *args): print("[MOCK] start", args)
        def set_controls(self, *args): print("[MOCK] set_controls", args)
    Picamera2 = MockCamera
class PiHardware:
    def __init__(self) -> None:
        self.current_x = 0 
        self.current_y = 0 
        self.x_neg_boundary = 0 
        self.y_neg_boundary = 0 
        self.x_pos_boundary = 0 
        self.y_pos_boundary = 0 


        self.camera = Picamera2()
        self.camera.start()
        self.camera.set_controls({"AfMode": 2})
        self.step_1 = 20
        self.step_2 = 21
        self.dir_1 = 26
        self.dir_2 = 19
        pins = [self.step_1, self.step_2, self.dir_1, self.dir_2]
        GPIO.setmode(GPIO.BCM)
        for pin in pins:
            GPIO.setup(pin, GPIO.OUT)

    def step(self, step_pin, dir_pin, steps, direction, delay=0.0005):
        GPIO.output(dir_pin, direction)

        for _ in range(steps):
            GPIO.output(step_pin, GPIO.HIGH)
            time.sleep(delay)   # HIGH time
            GPIO.output(step_pin, GPIO.LOW)
            time.sleep(delay)   # LOW time
    def step_x_pos(self, steps):
        self.step(self.step_1, self.dir_1, steps, GPIO.HIGH)
    def step_y_pos(self, steps):
        self.step(self.step_2, self.dir_2, steps, GPIO.HIGH)
    def step_x_neg(self, steps):
        self.step(self.step_1, self.dir_1, steps, GPIO.LOW)
    def step_y_neg(self, steps):
        self.step(self.step_2, self.dir_2, steps, GPIO.LOW)
