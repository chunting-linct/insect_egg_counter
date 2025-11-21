from flask import current_app as app, render_template, Response
from PIL import Image
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
import time
import io
current_x = 0 
current_y = 0 
x_neg_boundary = 0 
y_neg_boundary = 0 
x_pos_boundary = 0 
y_pos_boundary = 0 


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

def step(step_pin, dir_pin, steps, direction, delay=0.0005):
    GPIO.output(dir_pin, direction)

    for _ in range(steps):
        GPIO.output(step_pin, GPIO.HIGH)
        time.sleep(delay)   # HIGH time
        GPIO.output(step_pin, GPIO.LOW)
        time.sleep(delay)   # LOW time

@app.route("/snapshot")
def snapshot():
    # Capture an image
    img = camera.capture_array()  # numpy array

    # Convert to JPEG in memory
    pil_img = Image.fromarray(img).convert("RGB")
    buf = io.BytesIO()
    pil_img.save(buf, format='JPEG')
    buf.seek(0)
    return Response(buf.getvalue(), mimetype='image/jpeg')
def gen_frames():
    while True:
        img_array = camera.capture_array()
        pil_img = Image.fromarray(img_array).convert("RGB")
        buf = io.BytesIO()
        pil_img.save(buf, format='JPEG')
        frame = buf.getvalue()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route("/video_feed")
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route("/x/pos/<int:steps>")
def x_pos(steps):
    step(step_1, dir_1, int(steps), GPIO.HIGH) 

    global current_x
    current_x += steps
    return {"status": "ok", "steps": steps}

@app.route("/x/neg/<int:steps>")
def x_neg(steps):
    step(step_1, dir_1, steps, GPIO.LOW)
    global current_x
    current_x -= steps
    return {"status": "ok", "steps": steps}

@app.route("/y/pos/<int:steps>")
def y_pos(steps):
    step(step_2, dir_2, int(steps), GPIO.HIGH) 
    global current_y
    current_y += steps

    return {"status": "ok", "steps": steps}

@app.route("/y/neg/<int:steps>")
def y_neg(steps):
    step(step_2, dir_2, int(steps), GPIO.LOW) 
    global current_y
    current_y -= steps

    return {"status": "ok", "steps": steps}

@app.route("/y/pos/set")
def y_pos_set():
    
    global y_pos_boundary ,current_y
    y_pos_boundary= current_y
    print(y_pos_boundary)

    return {"status": "ok", "y": y_pos_boundary}
@app.route("/y/neg/set")
def y_neg_set():
    
    global y_neg_boundary ,current_y
    y_neg_boundary= current_y
    print(y_neg_boundary)

    return {"status": "ok", "y": y_neg_boundary}
@app.route("/x/pos/set")
def x_pos_set():
    
    global x_pos_boundary ,current_x
    x_pos_boundary= current_x
    print(x_pos_boundary)

    return {"status": "ok", "x": x_pos_boundary}
@app.route("/x/neg/set")
def x_neg_set():
    
    global x_neg_boundary ,current_x
    x_neg_boundary= current_x

    print(x_neg_boundary)
    return {"status": "ok", "x": x_neg_boundary}
@app.route("/")
def index():
    return render_template("index.html")
