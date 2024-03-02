# A simple script to calculate BMI
from pywebio.input import input, FLOAT
from pywebio.output import put_text
from pywebio import start_server

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

if __name__ == '__main__':
    start_server(bmi,port=1267)