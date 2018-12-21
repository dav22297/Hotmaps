import fiona
import pandas as pd
import numpy as np
from pyproj import Proj, transform
import os


path = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))))

path = os.path.join(path, "result")
point_path = os.path.join(path, "d412738e-2d70-4d97-b64c-e082de51bb32.shp")
points = fiona.open(point_path)
heat_demand_path = os.path.join(path, "0ef359f6-0f9d-445f-9c30-8c9462291d8c.csv")
heat_demand = pd.read_csv(heat_demand_path)



inProj = Proj(init='epsg:3035')
outProj = Proj(init='epsg:4326')

coordinates_of_points = []
for point in points:
    coordinates_of_points.append(transform(inProj, outProj, *point["geometry"]["coordinates"]))

total_heat_demand = np.sum(heat_demand["heat demand total 1st year [MWh]"].values)

demand_of_each_point = [total_heat_demand/len(coordinates_of_points)] * len(coordinates_of_points)

data = pd.DataFrame(coordinates_of_points, columns=("Lon", "Lat"))
data["Heat demand"] = demand_of_each_point
print(data)

