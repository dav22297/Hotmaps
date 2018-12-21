from scipy.stats import linregress
import numpy as np
import matplotlib.pyplot as plt
from operator import add
from igraph import *
from graphs import NetworkGraph
import pandas as pd

source_sink_connections = [[0], [1]]
source_source_connections = [[1], [0]]
sink_sink_connections = [[], []]
source_sink_distances = [[3], [5]]
source_source_distances = [[1], [1]]
sink_sink_distances = [[], []]
source_correspondence = [1,2]
sink_correspondence = [1,2]

graph = NetworkGraph(source_sink_connections, source_source_connections, sink_sink_connections, source_correspondence, sink_correspondence)

print(graph.correspondence_graph)


graph.add_edge_attribute("distance", source_sink_distances, source_source_distances, sink_sink_distances)
print(graph.correspondence_graph.es["distance"])

graph.reduce_to_minimum_spanning_tree("distance")
print(graph.correspondence_graph)
print(graph.max_flow_graph)
print(graph.graph)
print(graph.maximum_flow(np.array([1, 2]), np.array([2, 1])))

"""
#graph.plot([(0,0), (1, 0)], [(0, +1), (1, +1)])

print(graph.graph.es["distance"])

graph.delete_edges([(0,1)])
print(graph.maximum_flow(np.array([0.001, 0.002]), np.array([0.002, 0.001])))
print(graph.return_edge_source_target_vertices())
print(graph.max_flow_graph)

a = np.array([[0,1,2], [0,1,2]])
b = np.array([[0,1,2], [0,1,2]])
for i, c in enumerate(zip(a,b)):
    print(i, c)
"""