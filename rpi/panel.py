# A simple script to calculate BMI
from pywebio.input import input, FLOAT
from pywebio.output import put_text
from pywebio import start_server
from pywebio.output import use_scope, put_image, put_code
from pywebio.session import hold, set_env
from pywebio.pin import put_select, pin_wait_change

import time
import camera

def bmi():
    #run_js('WebIO._state.CurrentSession.on_session_close(()=>{setTimeout(()=>˓→location.reload(), 4000})')

    height = input("Input your height(cm)", type=FLOAT)
    weight = input("Input your weight(kg)", type=FLOAT)
    BMI = weight / (height / 100) ** 2
    top_status = [(16, 'Severely underweight'), (18.5, 'Underweight'), (25, 'Normal'), (30, 'Overweight'),
                    (35, 'Moderately obese'), (float('inf'), 'Severely obese')]
    for top, status in top_status:
        if BMI <= top:
            put_text('Your actual BMI: %.1f. Category: %s' % (BMI, status))
            break

@use_scope("liveview", clear=True)
def put_liveview(img):
    put_image(img)

def preview_stream():
    put_select('Which_image', ('leah', 'alicia'), multiple=False, value='leah')
    #put_liveview('rpi/liveview/test.jpg')
    preview_cam = camera.Cam()
    preview_cam.run()
    img1 = open('rpi/liveview/test.jpg', 'rb').read()
    img2 = open('rpi/liveview/test2.png', 'rb').read()
    while True:
        #selection = pin_wait_change('Which_image')
        #if selection['value'] == 'leah':
        put_liveview(img1)
        time.sleep(0.3)
        #else:
            #put_liveview('rpi/liveview/test2.png')

        if preview_cam.flag_next_frame == 1:
            put_text(("NEXT FRAME"))
            put_liveview(img2)
            preview_cam.flag_next_frame = 0
            time.sleep(0.3)


def controls():
    set_env(output_animation=False)
    put_text('Liveview test')
    #put_liveview('rpi/liveview/test.jpg')
    preview_stream()


if __name__ == '__main__':
    start_server(controls,port=1267)