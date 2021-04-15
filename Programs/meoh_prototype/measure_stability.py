import time
import threading
from datetime import datetime
from gpiozero import LED

import board
import busio
import pigpio
import simple_pid
import PySimpleGUI as SG

import lib.sgp40
import lib.mprls
import lib.constants
import lib.data_util

FIELDNAMES = ['Timestamp', 'Rel. pressure (hPa)', 'Raw signal (-)']
PRECISIONS = [None, '{:.2f}', None]
LOG_INTERVAL = 1

PWM_PIN = 18
PWM_FREQ = 20000

VALVE1 = LED(4)

data_g = []

DUTY_IDLE = 0
DUTY_MEASUREMENT = 100
DUTY_ANALYSIS = 36.6
DUTY_REGENERATION = 80

DUTY_MAX = 0.7E06
DUTY_MIN = 0

TIME_MEASUREMENT = 15
TIME_ANALYSIS = 120
TIME_REGENERATION = 204.7
TIME_OFF = 20

old = str('00')

def setup_sensors():
    # Connect sensors through I2C
    global sgp40
    global mpr
    global pi
    pi = pigpio.pi()
    i2c = busio.I2C(board.SCL, board.SDA)
    sgp40 = lib.sgp40.SGP40(i2c)
    mpr = lib.mprls.MPRLS(i2c, psi_min=0, psi_max=25)
    mpr.zero(5)


def setup_file_logger():
    file_add = 'SS1'
    filename = 'logs_' + datetime.now().strftime('%y%m%d') + '_' + file_add
    file = lib.constants.LOC_DATA_STABILITY + filename + '.csv'

    global data_writer
    data_writer = lib.data_util.DataWriter(file, FIELDNAMES)
    data_writer.set_precision(FIELDNAMES[1], PRECISIONS[1])
    print('Saving log at ' + file)


def set_pwm(duty):
    if duty > 100:
        print("Error, duty cycle above 100%")
    else:
        duty = duty*DUTY_MAX/100
        duty = int(duty)
        pi.hardware_PWM(PWM_PIN, PWM_FREQ, duty)


def destroy():
    set_pwm(0)


def measure_gas_and_log_loop():
    # Loop measuring gas sensor and writing it to the log with pressure value
    data = dict.fromkeys(FIELDNAMES)  # Dictionary containing data for the fields given in fieldnames
    while True:
        data[FIELDNAMES[0]] = datetime.now().strftime(lib.constants.TIMESTAMP_FORMAT)
        data[FIELDNAMES[1]] = mpr.rel_pressure
        data[FIELDNAMES[2]] = sgp40.raw
        data_writer.write_data(data)
        print(data[FIELDNAMES[0]][:-7] + ' %.2f %d' % (data[FIELDNAMES[1]], data[FIELDNAMES[2]]))
        
        time.sleep(LOG_INTERVAL)

def new_day_check(old):
    new = datetime.now().strftime('%d')
    if old != new:
        print('New File')
        setup_file_logger()
    else:
        pass

def auto_measurement(cycles):
    count = 0
    if int(cycles) == 0:
        old = datetime.now().strftime('%d')
        set_pwm(DUTY_MEASUREMENT)
        time.sleep(10)
        set_pwm(DUTY_IDLE)
        time.sleep(0.1)
        VALVE1.on()
        time.sleep(0.1)
        set_pwm(DUTY_ANALYSIS)
        time.sleep(10)
        set_pwm(DUTY_REGENERATION)
        time.sleep(10)
        set_pwm(DUTY_IDLE)
        time.sleep(0.5*10)
        mpr.zero(0.25*10)
        time.sleep(0.25*10)
        VALVE1.off()
        time.sleep(0.1)
        new_day_check(old)
    elif int(cycles) < 0:
        print("Cycles must be positive Integer!")
    
    while count < int(cycles):
        old = datetime.now().strftime('%d')
        set_pwm(DUTY_MEASUREMENT)
        time.sleep(TIME_MEASUREMENT)
        set_pwm(DUTY_IDLE)
        time.sleep(0.1)
        VALVE1.on()
        time.sleep(0.1)
        set_pwm(DUTY_ANALYSIS)
        time.sleep(TIME_ANALYSIS)
        set_pwm(DUTY_REGENERATION)
        time.sleep(TIME_REGENERATION)
        set_pwm(DUTY_IDLE)
        time.sleep(0.5*TIME_OFF)
        mpr.zero(0.25*TIME_OFF)
        time.sleep(0.25*TIME_OFF)
        VALVE1.off()
        time.sleep(0.1)
        new_day_check(old)
        count = count + 1
        
    
        
        
if __name__ == '__main__':
    setup_sensors()
    setup_file_logger()
    threading.Thread(target=measure_gas_and_log_loop, daemon=True).start()

    layout = [[SG.Text('Duty Cycle [0-100]'), SG.In(size=(12, 1), key='DUTY'), SG.Button('SET')],
              [SG.Button('Valve open'), SG.Button('Valve close'), SG.Button('Zero',size=(5,1))],
              [SG.Text('Rounds:'), SG.In(size=(8,1), key='cycles'),SG.Button('Sample'), SG.Button('EXIT')]]
    
    window = SG.Window("Methanol Detector", layout)

    while True:
        event, values = window.read()
        if event == 'SET':
            set_pwm(float(values['DUTY']))
        if event == 'Sample':
            auto_measurement(float(values['cycles']))
        if event == 'Zero':
            mpr.zero(2)
        if event == 'Valve open':
            VALVE1.on()
        if event == 'Valve close':
            VALVE1.off()
        if event == "EXIT" or event == SG.WIN_CLOSED:
            break

    window.close()
    destroy()
