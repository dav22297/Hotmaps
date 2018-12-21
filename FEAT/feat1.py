import os
import sys
import time
import json
import copy

# add directory with all modules to PYTHONPATH
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if path not in sys.path:
    sys.path.insert(0, path)

import numpy as np
from AD.read_data import ad_industrial_database
from AD.read_data import ad_eper_35_30
from AD.read_data import ad_industry_profiles
from AD.read_data import ad_residential_heating_profile
from CM.CM1 import orthodrome_distance, approximate_distance
from CM.CM1 import temp_check, district_heating_initial_costs, district_heating_operational_costs
from graphs import NetworkGraph
# TODO Header?


def find_neighbours(sites1, sites2, lon1_header, lat1_header, lon2_header, lat2_header, temp1_header, temp2_header,
                    max_distance, network_temp, site1_condition, site2_condition, site1_site2_condition,
                    small_angle_approximation=False):
    # get indices of columns
    lon1_ind = sites1.columns.get_loc(lon1_header)
    lat1_ind = sites1.columns.get_loc(lat1_header)
    lon2_ind = sites2.columns.get_loc(lon2_header)
    lat2_ind = sites2.columns.get_loc(lat2_header)
    temp1_ind = sites1.columns.get_loc(temp1_header)
    temp2_ind = sites2.columns.get_loc(temp2_header)

    connections = []
    distances = []
    for site1 in sites1.values:
        connections.append([])
        distances.append([])
        coordinate1 = (site1[lon1_ind], site1[lat1_ind])
        temp1 = site1[temp1_ind]
        for i, site2 in enumerate(sites2.values):
            coordinate2 = (site2[lon2_ind], site2[lat2_ind])
            temp2 = site2[temp2_ind]
            # check if source and sink are close enough
            if small_angle_approximation is False:
                distance = orthodrome_distance(coordinate1, coordinate2)
            else:
                distance = approximate_distance(coordinate1, coordinate2)
            if distance <= max_distance:
                if temp_check(temp1, network_temp, site1_condition) and \
                        temp_check(temp2, network_temp, site2_condition) and \
                        temp_check(temp1, temp2, site1_site2_condition):
                    connections[-1].append(i)
                    distances[-1].append(distance)

    return connections, distances


def create_normalized_profiles(profiles, region_header, time_header, value_header):
    """
    function normalizing profiles so that the sum of values over all time stamps of each region is 1

    :param profiles: dataframe containing profiles of different regions.
    :type profiles: pandas dataframe.
    :param region_header: header indicating the column containing the names of the regions.
    :type region_header: str.
    :param time_header: header indicating the column containing the time stamps of the profiles.
    :type time_header: str.
    :param value_header: header indicating the column containing the value of the profile.
    :type value_header: str.
    :return: list containing normalized profiles in form of numpy arrays. The keys are the region names.
    :rtype: dictionary {region_name: np.array(profile), region_name2: np.array(profile2), ...}
    """

    normalized_profiles = dict()
    regions = profiles[region_header].unique()
    for region in regions:
        profile = profiles.loc[profiles[region_header] == region]
        profile = profile.sort_values(time_header)
        profile = np.array(profile[value_header].values)
        profile = profile / np.sum(profile)
        normalized_profiles[region] = profile

    return normalized_profiles


def moving_average(array, order):
    """
    returns the moving average of the specified order.

    :param array: array of which the moving average should be computed.
    :type array: array like.
    :param order: order of moving average.
    :type order: int.
    :return: moving average of array.
    :rtype: array of same length as the input array.
    """
    return np.convolve(array, [1] * order) / order


def cost_of_connection(connection_distance, hourly_heat_flow, order=24):
    """
    function estimating the cost of an air to liquid heat exchanger.

    :param connection_distance: distance of the pipe in meters.
    :type connection_distance: float.
    :param hourly_heat_flow: hourly heat flow in MW.
    :type hourly_heat_flow: array like.
    :param order: specifies how many hours should be used for the moving average.
    :type order: int.
    :return: cost of heat exchanger in €.
    :rtype: float.
    """
    pipe_capacities = [0.2, 0.3, 0.6, 1.2, 1.9, 3.6, 6.1, 9.8, 20, 45, 75, 125, 190, 1e19]
    pipe_costs = [195, 206, 220, 240, 261, 288, 323, 357, 426, 564, 701, 839, 976, 976]
    capacity = np.max(moving_average(hourly_heat_flow, order))
    # create boolean array and np.argmax will return the index of the first True, hence the first pipe capacity
    # exceeding the required capacity
    pipe = int(np.argmax(pipe_capacities >= capacity)) - 1
    pipe_cost = pipe_costs[pipe]

    return pipe_cost * connection_distance


def cost_of_heat_exchanger_source(hourly_heat_flow, order=24):
    """
    function estimating the cost of an air to liquid heat exchanger.

    :param hourly_heat_flow: hourly heat flow in MW.
    :type hourly_heat_flow: array like.
    :param order: specifies how many hours should be used for the moving average.
    :type order: int.
    :return: cost of heat exchanger in €.
    :rtype: float.
    """
    return np.max(moving_average(hourly_heat_flow, order)) * 15000


def cost_of_heat_exchanger_sink(hourly_heat_flow, order=24):
    """
    function estimating the cost of an air to liquid heat exchanger.

    :param hourly_heat_flow: hourly heat flow in MW.
    :type hourly_heat_flow: array like.
    :param order: specifies how many hours should be used for the moving average.
    :type order: int.
    :return: cost of heat exchanger in €.
    :rtype: float.
    """
    capacity = np.max(moving_average(hourly_heat_flow, order))

    if capacity < 1:
        return capacity * (265000 + 240000)
    else:
        return capacity * (100000 + 90000)


if __name__ == "__main__":
    start = time.perf_counter()

    industrial_subsector_map = {"Iron and steel": "iron_and_steel", "Refineries": "chemicals_and_petrochemicals",
                                "Chemical industry": "chemicals_and_petrochemicals", "Cement": "non_metalic_minerals",
                                "Glass": "non_metalic_minerals",
                                "Non-metallic mineral products": "non_metalic_minerals", "Paper and printing": "paper",
                                "Non-ferrous metals": "iron_and_steel", "Other non-classified": "food_and_tobacco"}

    # load heat source and heat sink data
    heat_sources = ad_industrial_database()
    heat_sinks = ad_eper_35_30()
    print("sites loaded" + " " + str(time.perf_counter() - start))

    # load heating profiles for sources and sinks
    industry_profiles = ad_industry_profiles()
    residential_heating_profile = ad_residential_heating_profile()
    print("profiles loaded" + " " + str(time.perf_counter() - start))

    # normalize loaded profiles
    normalized_heat_profiles = dict()
    normalized_heat_profiles["residential_heating"] = create_normalized_profiles(residential_heating_profile,
                                                                                 "country", "hour", "load")
    for industry_profile in industry_profiles:
        normalized_heat_profiles[industry_profile.iloc[1]["process"]] = \
            create_normalized_profiles(industry_profile, "country", "hour", "load")
    print("profiles normalized" + " " + str(time.perf_counter() - start))

    # drop all sources with unknown or invalid nuts id
    heat_sources = heat_sources[heat_sources.Nuts0_ID != ""]
    heat_sources = heat_sources.dropna()
    for sub_sector in industrial_subsector_map:
            missing_profiles = list(set(heat_sources[heat_sources.Subsector == sub_sector]["Nuts0_ID"].unique()) -
                                    set(normalized_heat_profiles[industrial_subsector_map[sub_sector]].keys()))
            for missing_profile in missing_profiles:
                heat_sources = heat_sources[((heat_sources.Nuts0_ID != missing_profile) |
                                             (heat_sources.Subsector != sub_sector))]

            print("could not find profiles for heat sources with profile: " + str(sub_sector) + ":")
            print(missing_profiles)

    # drop all sinks with unknown or invalid nuts id
    heat_sinks = heat_sinks[heat_sinks.Nuts2_ID != ""]
    heat_sinks = heat_sinks.dropna()
    # find nuts ids of sites which do not have profiles
    missing_profiles = list(set(heat_sinks["Nuts2_ID"].unique()) -
                            set(normalized_heat_profiles["residential_heating"].keys()))
    for missing_profile in missing_profiles:
        heat_sinks = heat_sinks[heat_sinks.Nuts2_ID != missing_profile]

    print("could not find profiles for heat sinks:")
    print(missing_profiles)
    print("sites with these Nuts IDs will not be accounted for")

    # generate profiles for all heat sources and store them in an array
    heat_source_profiles = []
    heat_source_coordinates = []
    for _, heat_source in heat_sources.iterrows():
        heat_source_profiles.append(normalized_heat_profiles[industrial_subsector_map[heat_source["Subsector"]]]
                                    [heat_source["Nuts0_ID"]] * heat_source["Excess_heat"])
        heat_source_coordinates.append((heat_source["Lon"], heat_source["Lat"]))
    heat_source_profiles = np.array(heat_source_profiles)
    heat_source_profiles = heat_source_profiles.transpose()

    # generate profiles for all heat sinks and store them in an array
    heat_sink_profiles = []
    heat_sink_coordinates = []
    for _, heat_sink in heat_sinks.iterrows():
        heat_sink_profiles.append(normalized_heat_profiles["residential_heating"][heat_sink["Nuts2_ID"]] *
                                  heat_sink["Heat_demand"])
        heat_sink_coordinates.append((heat_sink["Lon"], heat_sink["Lat"]))
    heat_sink_profiles = np.array(heat_sink_profiles)
    heat_sink_profiles = heat_sink_profiles.transpose()
    print("hourly profiles of sources and sinks computed" + " " + str(time.perf_counter() - start))

    temperature = 100
    source_sink_connections, source_sink_distances = find_neighbours(
        heat_sources, heat_sinks, "Lon", "Lat", "Lon", "Lat", "Temperature", "Temperature", 20,
        temperature, "true", "true", "true", small_angle_approximation=True)
    source_source_connections, source_source_distances = find_neighbours(
        heat_sources, heat_sources, "Lon", "Lat", "Lon", "Lat", "Temperature", "Temperature", 20,
        temperature, "true", "true", "true", small_angle_approximation=True)
    sink_sink_connections, sink_sink_distances = find_neighbours(
        heat_sinks, heat_sinks, "Lon", "Lat", "Lon", "Lat", "Temperature", "Temperature", 20,
        temperature, "true", "true", "true", small_angle_approximation=True)

    print(source_source_connections)
    network = NetworkGraph(source_sink_connections, source_source_connections, sink_sink_connections,
                           range(len(source_source_connections)), range(len(sink_sink_connections)))
    print(network.graph)
    network.add_edge_attribute("distance", source_sink_distances, source_source_distances, sink_sink_distances)
    # reduce to minimum spanning tree
    network.reduce_to_minimum_spanning_tree("distance")

    source_flows = []
    sink_flows = []
    connection_flows = []
    for heat_source_capacities, heat_sink_capacities in zip(heat_source_profiles, heat_sink_profiles):
        source_flow, sink_flow, connection_flow = network.maximum_flow(heat_source_capacities, heat_sink_capacities)
        source_flows.append(source_flow)
        sink_flows.append(sink_flow)
        connection_flows.append(connection_flow)

    print(connection_flows)
    source_flows = np.array(source_flows)
    sink_flows = np.array(sink_flows)
    connection_flows = np.array(connection_flows)
    source_flows = source_flows.transpose()
    sink_flows = sink_flows.transpose()
    connection_flows = connection_flows.transpose()

    heat_exchanger_source_costs = []
    for flow in source_flows:
        heat_exchanger_source_costs.append(cost_of_heat_exchanger_source(flow))
    heat_exchanger_sink_costs = []
    for flow in sink_flows:
        heat_exchanger_sink_costs.append(cost_of_heat_exchanger_sink(flow))
    connection_lengths = network.get_edge_attribute("distance")
    connection_costs = []
    for flow, length in zip(connection_flows, connection_lengths):
        connection_costs.append(cost_of_connection(length, flow))

    heat_exchanger_source_cost_total = np.sum(heat_exchanger_source_costs)
    heat_exchanger_sink_cost_total = np.sum(heat_exchanger_sink_costs)
    connection_cost_total = np.sum(connection_costs)
    total_cost_scalar = heat_exchanger_sink_cost_total + heat_exchanger_source_costs + connection_cost_total
    total_flow_scalar = np.sum(source_flows)

    print("maximaum flow computed" + " " + str(time.perf_counter() - start))
