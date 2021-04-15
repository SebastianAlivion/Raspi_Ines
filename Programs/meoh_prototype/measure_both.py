from datetime import datetime

import board
import busio

import lib.constants
import lib.data_util
import lib.mprls
import lib.sgp40

FIELDNAMES = ['Timestamp', 'Rel. pressure (hPa)', 'Raw signal (-)']
PRECISIONS = [None, '{:.2f}', None]
SAMPLING_INTERVAL = 1


if __name__ == '__main__':
    # Setup file logger
    file_add = input('Measurement name: ')
    filename = 'log_' + datetime.now().strftime('%y%m%d') + '_' + file_add
    file = lib.constants.LOC_DATA_COMBINED + filename + '.csv'
    file_logger = lib.data_util.DataWriter(file, FIELDNAMES)
    file_logger.set_precision(FIELDNAMES[1], PRECISIONS[1])
    print('Saving log at ' + file)

    # Setup sensors
    i2c = busio.I2C(board.SCL, board.SDA)
    gas_sensor = lib.sgp40.SGP40(i2c)
    pressure_sensor = lib.mprls.MPRLS(i2c, psi_min=0, psi_max=25)
    pressure_sensor.zero(2)

    # Start measurement loop
    data = {}
    try:
        while True:
            data[FIELDNAMES[0]] = datetime.now().strftime(lib.constants.TIMESTAMP_FORMAT)
            data[FIELDNAMES[1]] = pressure_sensor.avgRelPressure(1)
            data[FIELDNAMES[2]] = gas_sensor.raw
            file_logger.write_data(data)
            print(data[FIELDNAMES[0]][:-7] + ' %.2f %d' % (data[FIELDNAMES[1]], data[FIELDNAMES[2]]))
    except KeyboardInterrupt:
        print('Measurement stopped')
