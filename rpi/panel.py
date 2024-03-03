# A simple script to calculate BMI
from pywebio.input import input, FLOAT
from pywebio.output import put_text
from pywebio import start_server
from pywebio.output import use_scope, put_image, put_code
from pywebio.session import hold, set_env
from pywebio.pin import put_select, pin_wait_change

import time, camera

@use_scope("liveview", clear=True)
def put_liveview(img):
    put_image(img)

def preview_stream():
    put_select('Which_image', ('leah', 'alicia'), multiple=False, value='leah')

    preview_cam = camera.Cam()
    preview_cam.run()
    img1 = open('rpi/liveview/test.jpg', 'rb').read()
    img2 = open('rpi/liveview/test2.png', 'rb').read()

    while True:
        put_liveview(img1)
        time.sleep(0.3)


def controls():
    set_env(output_animation=False)
    put_text('Liveview test')

    preview_stream()


if __name__ == '__main__':
    start_server(controls,port=1267)