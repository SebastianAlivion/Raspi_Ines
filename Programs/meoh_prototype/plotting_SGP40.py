import lib.plotting
import lib.constants

filename = lib.constants.LOC_DATA_COMBINED + input('Open file (filename): ') + '.csv'
cut = float(input('Plot duration (min): '))

plot = lib.plotting.SensorPlot(filename, 'Raw signal (-)', cut)
plot.setLabel('Time (min)', 'Raw signal (-)')
plot.set_ylim(lib.constants.SGP40_YLIM)
plot.show()
