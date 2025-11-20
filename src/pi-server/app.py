from flask import Flask, Response,request, jsonify, send_from_directory
from picamera2 import Picamera2
from libcamera import controls
import RPi.GPIO as GPIO
from PIL import Image
import time
import io

camera = Picamera2()
camera.start()
camera.set_controls({"AfMode": 2})
time.sleep(1)
app = Flask(__name__)
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
    from PIL import Image
    import numpy as np

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
@app.route("/")
def index():
    return send_from_directory("static", "index.html")
@app.route("/x/pos/<steps>")
def x_pos(steps):
    step(step_1, dir_1, int(steps), GPIO.HIGH) 

    return f"<p>x pos Step {steps}</p>"

@app.route("/x/neg/<steps>")
def x_neg(steps):
    step(step_1, dir_1, int(steps), GPIO.LOW) 

    return f"<p>x neg Step {steps}</p>"

@app.route("/y/pos/<steps>")
def y_pos(steps):
    step(step_2, dir_2, int(steps), GPIO.HIGH) 

    return f"<p>y pos Step {steps}</p>"

@app.route("/y/neg/<steps>")
def y_neg(steps):
    step(step_2, dir_2, int(steps), GPIO.LOW) 

    return f"<p>y neg Step {steps}</p>"
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

