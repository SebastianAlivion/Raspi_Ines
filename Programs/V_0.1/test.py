""" Example for using the SGP30 with CircuitPython and the Adafruit library"""

import time
from datetime import datetime
import board
import busio
import adafruit_sgp30

TIMESTAMP_FORMAT = "%Y-%m-%d_%H:%M:%S"
LOG_FILE_LOC = "log_" + datetime.now().strftime("%y%m%d") + ".txt"

def connect_sensor():
    i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
    sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)
    return sgp30

def initiate_sensor():
    sgp30.iaq_init()
    set_baseline()

def read_baseline():
    with open(baseline_file_loc, "r") as f:
        last_line = f.readlines()[-1]
    timestamp = datetime.strptime(last_line.split()[0], TIMESTAMP_FORMAT)
    base_CO2 = int(last_line.split()[1], 16)
    base_tVOC = int(last_line.split()[2], 16)
    return [timestamp, base_CO2, base_tVOC]

def set_baseline():
    try:
        baseline = read_baseline()
        age = datetime.now() - baseline[0]
        if age.days < 7:
            sgp30.set_iaq_baseline(baseline[1], baseline[2])
            print("Baseline set: " + " ".join([str(i) for i in baseline]))
        else:
            raise RuntimeError("Sensor must be burned in again for 12 hours!")
    except FileNotFoundError:
        print("Sensor must be burned in initially for 12 hours!")
        quit()
        
def write_baseline():
    baseline = sgp30.get_iaq_baseline()
    with open(baseline_file_loc, "a") as f:
        f.write(datetime.now().strftime(TIMESTAMP_FORMAT) + " 0x%x 0x%x\n" % (baseline[0], baseline[1]))
        
def write_data(timestamp, data_iaq, data_raw):
    with open(LOG_FILE_LOC, "a") as f:
        f.write(timestamp.strftime(TIMESTAMP_FORMAT) + " %d %d %d %d\n" % (data_iaq[0], data_iaq[1], data_raw[0], data_raw[1]))
   
timer_log = 0
max_log = 60*60
        
sgp30 = connect_sensor()
baseline_file_loc = "baseline_" + "_".join([hex(i) for i in sgp30.serial]) + ".txt"
print(baseline_file_loc)
initiate_sensor()

while True:
    data_iaq = sgp30.iaq_measure()
    data_raw = sgp30.raw_measure()
    timestamp = datetime.now()
    write_data(timestamp, data_iaq, data_raw)
    print(timestamp.strftime(TIMESTAMP_FORMAT) + " %d %d %d %d" % (data_iaq[0], data_iaq[1], data_raw[0], data_raw[1]))
    time.sleep(1)
    timer_log += 1
    # Log baseline once per hour
    if timer_log >max_log:
        timer_log = 0
        write_baseline()
