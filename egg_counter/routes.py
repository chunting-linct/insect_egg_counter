from flask import current_app as app, render_template, Response, send_file
from PIL import Image
from .pi_hardware import PiHardware
import io
import os
import zipfile

pi_hardware = PiHardware()

@app.route("/snapshot")
def snapshot():
    # Capture an image
    img = pi_hardware.camera.capture_array()  # numpy array

    # Convert to JPEG in memory
    pil_img = Image.fromarray(img).convert("RGB")
    buf = io.BytesIO()
    pil_img.save(buf, format='JPEG')
    buf.seek(0)
    return Response(buf.getvalue(), mimetype='image/jpeg')
def gen_frames():
    while True:
        img_array = pi_hardware.camera.capture_array()
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
    pi_hardware.step_x_pos(steps)
    pi_hardware.current_x += steps
    return {"status": "ok", "steps": steps}

@app.route("/x/neg/<int:steps>")
def x_neg(steps):
    
    pi_hardware.step_x_neg(steps)
    pi_hardware.current_x -= steps
    return {"status": "ok", "steps": steps}

@app.route("/y/pos/<int:steps>")
def y_pos(steps):
    pi_hardware.step_y_pos(steps)
    pi_hardware.current_y += steps

    return {"status": "ok", "steps": steps}

@app.route("/y/neg/<int:steps>")
def y_neg(steps):
    pi_hardware.step_y_neg(steps)
    pi_hardware.current_y -= steps

    return {"status": "ok", "steps": steps}

@app.route("/y/pos/set")
def y_pos_set():
    
    pi_hardware.y_pos_boundary= pi_hardware.current_y
    pi_hardware.camera.capture_file('egg_counter/static/boundary/right_boundary.jpg')

    return {"status": "ok", "y": pi_hardware.y_pos_boundary}
@app.route("/y/neg/set")
def y_neg_set():
    
    pi_hardware.y_neg_boundary= pi_hardware.current_y
    pi_hardware.camera.capture_file('egg_counter/static/boundary/left_boundary.jpg')

    return {"status": "ok", "y": pi_hardware.y_neg_boundary}
@app.route("/x/pos/set")
def x_pos_set():
    
    pi_hardware.x_pos_boundary= pi_hardware.current_x
    pi_hardware.camera.capture_file('egg_counter/static/boundary/down_boundary.jpg')

    return {"status": "ok", "x": pi_hardware.x_pos_boundary}
@app.route("/x/neg/set")
def x_neg_set():
    
    
    pi_hardware.x_neg_boundary= pi_hardware.current_x
    pi_hardware.camera.capture_file('egg_counter/static/boundary/up_boundary.jpg')

    return {"status": "ok", "x": pi_hardware.x_neg_boundary}
@app.route("/start_scan")
def start_scan():
    error = pi_hardware.move_to_start_point()
    if error :
        return error
    folder = os.path.join(app.root_path, "static/result_pictures")
    pi_hardware.scan_and_capture(folder)
    return {"status": "ok"}
    
@app.route("/")
def index():
    return render_template("index.html")
@app.route("/browse")
def browse():
    folder = os.path.join(app.root_path, "static/result_pictures")
    images =  [file for file in os.listdir(folder) if file.endswith('.jpg')]
    return render_template("browse.html", images=images)

@app.route("/download_all")
def download_all():

    folder = os.path.join(app.root_path, "static/result_pictures")
    # Create zip file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as z:
        for filename in os.listdir(folder):
            full_path = os.path.join(folder, filename)
            z.write(full_path, arcname=filename)

    zip_buffer.seek(0)

    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name="images.zip",
        mimetype="application/zip",
    )
