import time
from datetime import datetime

import board
import busio

import lib.constants
import lib.data_util
import lib.sgp40

# Connect sensor through I2C
i2c = busio.I2C(board.SCL, board.SDA)
sgp40 = lib.sgp40.SGP40(i2c)

# Set name for log file
file_add = input('Measurement name: ')
filename = "log_" + datetime.now().strftime("%y%m%d") + "_" + file_add
file = lib.constants.LOC_DATA_SGP40 + filename + '.csv'
print('Saving log at ' + file)

fieldnames = ['Timestamp', 'Raw signal (-)']

data_writer = lib.data_util.DataWriter(file, fieldnames)

data = {}
while True:
    data[fieldnames[0]] = datetime.now().strftime(lib.constants.TIMESTAMP_FORMAT)
    data[fieldnames[1]] = sgp40.raw
    data_writer.write_data(data)
    print(data[fieldnames[0]][:-7] + " %d" % data[fieldnames[1]])
    time.sleep(1)
