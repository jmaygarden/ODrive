#!/usr/bin/env python

import matplotlib.pyplot as plot
import numpy as np

data = []

with open("oscilloscope.csv") as fin:
    data = np.array([float(line.strip()) for line in fin.readlines()][:8000])

t = np.linspace(0, data.shape[0] / 8000.0, data.shape[0])

plot.plot(t, data)
plot.title("Acceleration Feed-Forward Term (Gain = 0.8)")
plot.xlabel("Time (s)")
plot.ylabel("Current (A)")
plot.show()

