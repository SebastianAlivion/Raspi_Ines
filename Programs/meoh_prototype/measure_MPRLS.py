from datetime import datetime

import board
import busio

import lib.constants
import lib.data_util
import lib.mprls

# Connect sensor through I2C
i2c = busio.I2C(board.SCL, board.SDA)
mpr = lib.mprls.MPRLS(i2c, psi_min=0, psi_max=25)

# Set name for log file
filename = "log_" + datetime.now().strftime("%y%m%d")
file = lib.constants.LOC_DATA_MPRLS + filename + '.csv'
print('Saving log at ' + file)

fieldnames = ['Timestamp', 'Rel. Pressure (hPa)']  # Fields to be written in CSV file
precision = '{:.2f}'  # Precision which data is written (2 decimal float)

# Set up CSV file writer
file_writer = lib.data_util.DataWriter(file, fieldnames)
file_writer.set_precision(fieldnames[1], precision)

# Determine the baseline pressure
print("Determining baseline pressure...")
mpr.zero(5)

data = dict.fromkeys(fieldnames)  # Dictionary containing data for the fields given in fieldnames

# Main loop measuring pressure and writing it to the log
while True:
    data[fieldnames[0]] = datetime.now().strftime(lib.constants.TIMESTAMP_FORMAT)
    data[fieldnames[1]] = mpr.avgRelPressure(0.5)
    file_writer.write_data(data)
    print(data[fieldnames[0]][:-7] + " %.2f" % data[fieldnames[1]])
