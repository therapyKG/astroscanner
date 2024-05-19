from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO
from apscheduler.schedulers.background import BackgroundScheduler
from camera import Cam
import time, atexit, cv2, tifffile, rawdev, motor, gpiozero
import numpy as np

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)

cam = Cam()

Relay_Ch1 = 26
Relay_Ch2 = 20
Relay_Ch3 = 21

backlight = gpiozero.LED(Relay_Ch3)

@app.route('/', methods=["POST", "GET"])
def home():
    return render_template("liveview.html")

def update_temp():
    socketio.emit("temp_update", {"data": cam.get_temp()})

def update_expo():
    socketio.emit("expo_update", {"data": cam.get_shutter_speed()/1000})
    
def update_liveview():
    if cam.has_new:
        #tifffile.imwrite("./captures/raw_binned_"+ str(self.total) +".tif", binned_img.astype('uint16'), photometric='rgb')
        _, encoded_img = cv2.imencode('.jpg', cam.binned/256)
        socketio.emit("liveview_update", {"data": encoded_img.tobytes()})
        cam.has_new = False

@socketio.on("lv_polling")
def lv_polling():
    update_liveview()

@socketio.on("go_up")
def go_up():
    motor.z_move('up')

@socketio.on("go_down")
def go_down():
    motor.z_move('down')

@socketio.on("expo_up")
def expo_up():
    cam.set_shutter_speed(cam.get_shutter_speed() + 10000)

@socketio.on("expo_down")
def expo_down():
    cam.set_shutter_speed(cam.get_shutter_speed() - 10000)

@socketio.on("focus")
def focus():
    cam.start_focus = True

@socketio.on("lightswitch")
def lightswitch():
    if backlight.is_active:
        backlight.off()
    else: backlight.on()

@socketio.on("saveslice")
def saveslice():
    print("SAVE DTYPE: " + str(cam.binned.dtype))
    tifffile.imwrite("rpi/captures/raw_binned_"+ str(cam.total) +".tif", cam.binned.astype('uint16'), photometric='rgb')

scheduler = BackgroundScheduler()
scheduler.add_job(update_temp, "interval", seconds = 2)
scheduler.add_job(update_expo, "interval", seconds = 2)
#lv_update = scheduler.add_job(update_liveview, "interval", seconds = 1)

atexit.register(lambda: scheduler.shutdown())
atexit.register(lambda: cam.shutdown())

if __name__ == '__main__':
    motor.init()
    cam.run()
    cam.pull_high_res()
    scheduler.start()
    socketio.run(app, host = '192.168.50.23', port = 5000)