import os
import csv
import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


def wurzel_funktion(x, a, b, c):
    return a*x**b + c

def log_funktion(x, a, b, c, d):
    return a*np.log(x+d)/np.log(b) + c

def poly_2(x, a, b, c):
    return a*x**2 + b*x + c

def poly_3(x, a, b, c, d):
    return a*x**3 + b*x**2 + c*x + d

def poly_4(x, a, b, c, d, e):
    return a*x**4 + b*x**3 + c*x**2 + d*x + e

path = os.path.dirname(
       os.path.dirname(
       os.path.dirname(os.path.abspath(__file__))))
path = os.path.join(os.path.join(path, "data"), "fernwaerme_leitungen.csv")

# determine delimiter of csv file
with open(path, 'r') as csv_file:
    delimiter = csv.Sniffer().sniff(csv_file.readline()).delimiter
data = pd.read_csv(path, sep=delimiter, encoding="ANSI")
pipe_types= ["Fernwärmeleitung,PE,6 bar,1-fach", "Fernwärmeleitung,PE,10 bar,1-fach", "Fernwärmeleitung,PE,6 bar,2-fach", "Fernwärmeleitung,PE,6,4-fach", "Fernwärmeleitung,PE,10,2-fach"]

weights = []
parameters = []
for pipe in pipe_types:
    x = []
    y = []
    flow_per_cost = []
    for i, row in data[data.Kurztext.str.contains(pipe)].iterrows():
        cost = row["Mittel"]
        cost = float(cost.replace(",", "."))
        m = re.search(r"(\d+)(?!.*\d)", row["Kurztext"])
        diameter = float(m.group(0))
        x.append(diameter**2)
        y.append(cost)
        flow_per_cost.append(diameter**2/cost)
    p, coov = curve_fit(wurzel_funktion, x, y)
    print(p)
    weights.append(1/np.diagonal(coov))
    parameters.append(p)
    plot_range = np.linspace(np.min(x)*0.8, np.max(x)*1.2, num=256)
    plt.plot(plot_range, wurzel_funktion(plot_range, *p))
    plt.plot(plot_range, plot_range*y[-1]/x[-1])
    plt.plot(x, y, "o")
    plt.show()

