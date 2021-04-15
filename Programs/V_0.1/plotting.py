import time
from math import log
from math import exp
from datetime import datetime

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

TIMESTAMP_FORMAT = "%Y-%m-%d_%H:%M:%S"

def read(file):
    with open(file, "r") as f:
        data = [[],[]]
        first_line = f.readline()
        values = first_line.split()
        start_time = datetime.strptime(values[0], TIMESTAMP_FORMAT)
        while True:
            line = f.readline()
            if line:
                try:
                    values = line.split()
                    timestamp = datetime.strptime(values[0], TIMESTAMP_FORMAT)
                    diff = timestamp - start_time
                    data[0].append(diff.seconds/60)
                    if raw:
                        data[1].append(int(values[3]))
                    else:
                        data[1].append(int(values[1]))
                except:
                    pass
            else:
                yield data
                
                
def animate(values):
    x = values[0][-cut:]
    y = values[1][-cut:]
    y_max = max(y)
    y_min = min(y)
    line.set_data(x, y)
    ax.set_xlim(x[0], x[-1])
 #   if raw:        
  #      log_padding = 0.1*(log(y_max)-log(y_min))
  #      ax.set_ylim(exp(log(y_min)-log_padding), exp(log(y_max)+log_padding))
 #   else:
    padding = 0.1*(y_max-y_min)
    ax.set_ylim(y_min-padding, y_max+padding)    
    return line,

filename = input('Open file (filename): ')+'.txt'
cut = int(input('Plot duration (min): ')) * 60
raw = input("Show raw data: ") == "yes"

fig, ax = plt.subplots()
ax.set_xlabel('Time [min]')
#if raw:
#    ax.set_ylabel("Raw signal [-]")
#    ax.set_yscale('log')
#else:
ax.set_ylabel('TVOC [-]')
line, = ax.plot([])

ani = FuncAnimation(fig, animate, frames=read(filename), interval=1000)
plt.show()
