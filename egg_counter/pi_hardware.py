from logging import shutdown
import time
import os 
import numpy as np
import shutil
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
        def capture_file(self, *args): print("[MOCK] capture_file", args)
    Picamera2 = MockCamera
class PiHardware:
    def __init__(self) -> None:
        self.current_x = 0 
        self.current_y = 0 
        self.x_neg_boundary = None
        self.y_neg_boundary = None 
        self.x_pos_boundary = None 
        self.y_pos_boundary = None 


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
        
        
    def move_to_start_point(self):
        if self.x_neg_boundary == None or self.y_neg_boundary == None or self.x_pos_boundary ==None or self.y_pos_boundary == None:
            return {"error": "Boundary not set yet!"}
        x_movement = self.current_x - self.x_neg_boundary
        y_movement = self.current_y - self.y_neg_boundary
        self.step_x_neg(x_movement)
        self.step_y_neg(y_movement)
        return None

    def calculate_step_list(self):
        x_length = self.x_pos_boundary - self.x_neg_boundary
        y_length = self.y_pos_boundary - self.y_neg_boundary
        x_default_step = 50
        y_default_step = 30
        x_step_list = []
        y_step_list = []

        while x_length > x_default_step:
            x_step_list.append(x_default_step)
            x_length -= x_default_step
        x_step_list.append(x_length)

        while y_length > y_default_step:
            y_step_list.append(y_default_step)
            y_length -= y_default_step
        y_step_list.append(y_length)


        return x_step_list, y_step_list

    

    def scan_and_capture(self, path):
        flag = 1
        i = 1000
        if os.path.exists(path):
            shutil.rmtree(path)
        os.mkdir(path)
        x_step_list, y_step_list = self.calculate_step_list()

        for y_step in y_step_list:
            for x_step in x_step_list:
                time.sleep(0.5)
                self.camera.capture_file(os.path.join(path, f"{i}.jpg"))
                i += 1
                if flag == 1:
                    self.step_x_pos(x_step)
                else:
                    self.step_x_neg(x_step)
            time.sleep(0.5)
            self.camera.capture_file(os.path.join(path, f"{i}.jpg"))
            i += 1
            self.step_y_pos(y_step)
            flag *= -1
