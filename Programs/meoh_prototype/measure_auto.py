import time
import threading
from datetime import datetime

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
PID_INT = 0.1

data_g = []
pressure = 0

PRESSURE_IDLE = 0
PRESSURE_MEASUREMENT = -28
PRESSURE_ANALYSIS = -26.5
PRESSURE_REGENERATION = -150

TIME_MEASUREMENT = 10
TIME_ANALYSIS = 90
TIME_REGENERATION = 720

HEADS = 0
FEATURE1 = 0
FEATURE2 = 0
HOLD = 0
TESTMODE = 0

FASTP = 1

def initialize():
    HEADS = 0
    FEATURE1 = 0
    FEATURE2 = 0
    HOLD = 0
    TESTMODE = 0

def setup_sensors():
    # Connect sensors through I2C
    global sgp40
    global mpr
    i2c = busio.I2C(board.SCL, board.SDA)
    sgp40 = lib.sgp40.SGP40(i2c)
    mpr = lib.mprls.MPRLS(i2c, psi_min=0, psi_max=25)
    mpr.zero(2)


def setup_file_logger():
    file_add = input('Measurement name: ')
    filename = 'log_' + datetime.now().strftime('%y%m%d') + '_' + file_add
    file = lib.constants.LOC_DATA_COMBINED + filename + '.csv'

    global data_writer
    data_writer = lib.data_util.DataWriter(file, FIELDNAMES)
    data_writer.set_precision(FIELDNAMES[1], PRECISIONS[1])
    print('Saving log at ' + file)


def setup_PID():
    global pid
    global pi
    pid = simple_pid.PID(-500, -6500, -100)
    pid.output_limits = (0.15E6, 0.7E6)
#     pid.proportional_on_measurement = True
    pi = pigpio.pi()


def set_pwm(duty):
    if duty < 0.2E6:
        duty = 0
    pi.hardware_PWM(PWM_PIN, PWM_FREQ, duty)


def destroy():
    set_pwm(0)


def measure_gas_and_log_loop():
    # Loop measuring gas sensor and writing it to the log with pressure value
    data = dict.fromkeys(FIELDNAMES)  # Dictionary containing data for the fields given in fieldnames
    while True:
        data[FIELDNAMES[0]] = datetime.now().strftime(lib.constants.TIMESTAMP_FORMAT)
        data[FIELDNAMES[1]] = pressure
        data[FIELDNAMES[2]] = sgp40.raw
        data_writer.write_data(data)
        print(data[FIELDNAMES[0]][:-7] + ' %.2f %d' % (data[FIELDNAMES[1]], data[FIELDNAMES[2]]))
        time.sleep(LOG_INTERVAL)


def adjust_pressure_loop():
    global pressure
#     FastPressure
    if FASTP == 1:
        filename = 'log_' + datetime.now().strftime('%y%m%d') + '_' + 'pressure_fast'
        file = lib.constants.LOC_DATA_PRESSURE + filename + '.csv'
        writer = lib.data_util.DataWriter(file, ['Timestamp', 'Rel. pressure (hPa)'])
        writer.set_precision('Rel. pressure (hPa)', '{:.2f}')
        data = dict.fromkeys(['Timestamp', 'Rel. pressure (hPa)'])
    while True:
        pressure = mpr.rel_pressure
        duty = int(pid(pressure))
        set_pwm(duty)
        time.sleep(PID_INT)
#         FastPressure
        if FASTP == 1:
            data['Timestamp'] = datetime.now().strftime(lib.constants.TIMESTAMP_FORMAT)
            data['Rel. pressure (hPa)'] = pressure
            writer.write_data(data)


def set_setpoint(value):
    pid.setpoint = value


def auto_measurement():
    if HEADS == 1:
        headspace()
    elif HEADS == 2:
        vacuum()
    else:
        print("Choose sampling mode")
        
def headspace():
    set_setpoint(0)
    time.sleep(5)
    set_setpoint(PRESSURE_MEASUREMENT)
    time.sleep(TIME_MEASUREMENT)
    set_setpoint(PRESSURE_IDLE)
    time.sleep(5)
    set_setpoint(PRESSURE_ANALYSIS)
    time.sleep(TIME_ANALYSIS)
    set_setpoint(PRESSURE_REGENERATION)
    time.sleep(TIME_REGENERATION)
    set_setpoint(0)
    
def vacuum():
    pid.tunings = (-1000, -250, 0)
    set_setpoint(-300)
    while True:
        time.sleep(0.1)
        if pressure < -300:
            break
    pid.tunings = (-500, -6500, -100)
    if HOLD == 0:
        set_setpoint(0)
    
    if FEATURE1 and FEATURE2 == 1:
        reapply()
        stopdetection()
    elif FEATURE1 == 1:
        reapply()
    elif FEATURE2 == 1:
        stopdetection()
    
    if TESTMODE == 0:
        time.sleep(5)
        set_setpoint(PRESSURE_ANALYSIS)
        time.sleep(TIME_ANALYSIS)
        set_setpoint(PRESSURE_REGENERATION)
        time.sleep(TIME_REGENERATION)
        set_setpoint(0)

def reapply():
    pid.tunings = (-1000, -500, 0)
    set_setpoint(0)
    while True:
        time.sleep(0.1)
        if pressure > -210:
            set_setpoint(-300)
            while True:
                if pressure < -295:
                    break
            break
    pid.tunings = (-500, -6500, -100)
    
def stopdetection():
    while True:
        time.sleep(0.1)
        if pressure > -250:
            set_setpoint(0)
            break   


if __name__ == '__main__':
    setup_sensors()
    setup_PID()
    setup_file_logger()
    threading.Thread(target=adjust_pressure_loop, daemon=True).start()
    threading.Thread(target=measure_gas_and_log_loop, daemon=True).start()

    layout = [[SG.Text('Pressure'), SG.In(size=(10, 1), key='-PRESSURE-'), SG.Button('SET')],
              [SG.Button('Sample'), SG.Button('Zero'), SG.Button('EXIT')],
              [SG.Checkbox('Headspace', default=False, key='H'), SG.Checkbox('Vacuum', default=True,key='V')],
              [SG.Checkbox('Stop detection', default=True,key='S'), SG.Checkbox('Reapplying', key='R')],
              [SG.Checkbox('Pressure hold', default=True,key='P'), SG.Checkbox('Vacuum Test mode', key='T')]]
    
    window = SG.Window("Methanol Detector", layout)

    while True:
        event, values = window.read()
        if event == 'SET':
            set_setpoint(float(values['-PRESSURE-']))
        if event == 'Sample':
            if values['H'] == True:
                HEADS = 1
            if values['V'] == True:
                HEADS = 2
            if values['S'] == True:
                FEATURE2 = 1
            if values['R'] == True:
                FEATURE1 = 1
            if values['P'] == True:
                HOLD = 1
            if values['T'] == True:
                TESTMODE = 1
            auto_measurement()
            initialize()
        if event == 'Zero':
            mpr.zero(2)
        if event == "EXIT" or event == SG.WIN_CLOSED:
            break

    window.close()
    destroy()
