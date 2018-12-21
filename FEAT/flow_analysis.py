import json
import numpy as np
import matplotlib.pyplot as plt

with open("..\\max_flow.json") as json_file:
    data = json.load(json_file)

y = []
for hour in data[2]:
    y.append(hour[20:25])

plt.plot(range(8760), y)
plt.show()
