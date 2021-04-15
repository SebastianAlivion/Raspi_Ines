from datetime import datetime

import lib.plotting
import lib.constants

# Plot the current log
name = input('Filename: ')
file = lib.constants.LOC_DATA_COMBINED + name + '.csv'
print('Plotting from log ' + file)

cut = 2  # Plot the pressure history of the last 2 min

plot = lib.plotting.SensorPlot(file, 'Rel. pressure (hPa)', cut)
plot.setLabel('Time (min)', 'Rel. pressure (hPa)')
plot.ax.axhline(y=-25, color='r', linestyle='-')
plot.show()
