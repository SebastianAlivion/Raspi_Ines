import threading

import lib.plotting
import lib.constants


def plotSensor(file, key, cut, lim=(None, None)):
    plot = lib.plotting.SensorPlot(file, key, cut)
    plot.setLabel('Time (min)', key)
    plot.set_ylim(lim)
    return plot


if __name__ == '__main__':
    filename = lib.constants.LOC_DATA_COMBINED + input('Open file (filename): ') + '.csv'
    cut = float(input('Plot duration (min): '))
    plot1 = plotSensor(filename, 'Raw signal (-)', 30, lib.constants.SGP40_YLIM)
    plot2 = plotSensor(filename, 'Rel. pressure (hPa)', 20 / 60)
    # plot1.show()
    plot2.show()
