import time
from datetime import datetime, timedelta
import csv

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import lib.constants


class SensorPlot:

    def __init__(self, filename, field, cut, interval=1000):
        self.file = filename
        self.field = field
        self.cut = timedelta(minutes=cut)
        self.interval = interval
        self.ymin, self.ymax = None, None

        self.x_data = []
        self.y_data = []

        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot(self.x_data, self.y_data)

    def setLabel(self, xLabel, yLabel):
        self.ax.set_xlabel(xLabel)
        self.ax.set_ylabel(yLabel)

    def set_ylim(self, lim):
        self.ymin, self.ymax = lim

    def show(self):
        self.ani = FuncAnimation(self.fig, self.animate, frames=self.read(), interval=self.interval)
        plt.show()

    def read(self):
        with open(self.file) as f:
            fields = f.readline()[:-1].split(',')
            y_field = fields.index(self.field)
            while True:
                data = f.readline()[:-1].split(',')
                if data != ['']:
                    timestamp = datetime.strptime(data[0], lib.constants.TIMESTAMP_FORMAT)
                    self.x_data.append(timestamp)
                    self.y_data.append(float(data[y_field]))
                else:
                    yield

    def animate(self, i):
        x = [(i - self.x_data[0]).total_seconds() / 60 for i in self.x_data if i > self.x_data[-1] - self.cut]
        y = self.y_data[-len(x):]
        self.line.set_data(x, y)
        self.ax.set_xlim(x[0], x[-1])
        if not self.ymin:
            ymin = min(y)
        else:
            ymin = self.ymin
        if not self.ymax:
            ymax = max(y)
        else:
            ymax = self.ymax
        padding = (ymax - ymin) * 0.1
        self.ax.set_ylim(ymin - padding, ymax + padding)
