from datetime import datetime

import lib.plotting
import lib.constants

# Plot the current log
file = './data/pressure/pressure.csv'
print('Plotting from log ' + file)

cut = 0.5  # Plot the pressure history of the last 2 min

plot = lib.plotting.SensorPlot(file, 'Rel. pressure (hPa)', cut)
plot.setLabel('Time (min)', 'Rel. pressure (hPa)')
plot.ax.axhline(y=-25, color='r', linestyle='-')
plot.show()
