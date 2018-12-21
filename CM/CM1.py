from geopy.distance import distance
import numpy as np


def temp_check(temp_source, temp_sink, condition):
    """
    function determining if source can provide heat for a sink.

    :param temp_source: temperature of the heat source.
    :type temp_source: float.
    :param temp_sink: temperature of the heat sink.
    :type temp_sink: float.
    :param condition: determines condition the temperature check uses.
    :type condition: str of following list [">", ">=", "=", "<", "<=", "!=", "true", "false"].

    :return: returns true, if source can provide heat for sink.
    :rtype: bool.
    """

    if condition == ">":
        if temp_source > temp_sink:
            return True
        else:
            return False
    elif condition == ">=":
        if temp_source > temp_sink:
            return True
        else:
            return False
    elif condition == "=":
        if temp_source == temp_sink:
            return True
        else:
            return False
    elif condition == "<=":
        if temp_source <= temp_sink:
            return True
        else:
            return False
    elif condition == "<":
        if temp_source < temp_sink:
            return True
        else:
            return False
    elif condition == "!=":
        if temp_source != temp_sink:
            return True
        else:
            return False
    elif condition == "true":
        return True
    elif condition == "false:":
        return False


def orthodrome_distance(coordinate_1, coordinate_2, ellipsoid="WGS-84"):
    """
    function computing the geodesic distance of two points on an ellipsoid (aka orthodrome).

    :param coordinate_1: (longitude, latitude) of first location.
    :type coordinate_1: tuple(float, float).
    :param coordinate_2: (longitude, latitude) of second location.
    :type coordinate_2: tuple(float, float).
    :param ellipsoid: optional ellipsoid model used for computation of distance.
    :type ellipsoid: str {"WGS-84", "GRS_80", "Airy (1830)", "Intl 1924", "Clarke (1880)", "GRS-67"}.

    :return: orthodrome length in km.
    :rtype: float.
    """

    return distance(coordinate_1, coordinate_2, ellipsoid=ellipsoid).km


def approximate_distance(coordinate_1, coordinate_2):
    """
    function computing the approximate distance of two points  with small angle approximation.

    :param coordinate_1: (longitude, latitude) of first location.
    :type coordinate_1: tuple(float, float).
    :param coordinate_2: (longitude, latitude) of second location.
    :type coordinate_2: tuple(float, float).

    :return: distance in km.
    :rtype: float.
    """

    return np.sqrt((coordinate_2[0] - coordinate_1[0]) ** 2 + (coordinate_2[1] - coordinate_1[1]) ** 2) /\
           360 * 6378.137 * 2 * np.pi


def district_heating_initial_costs(length, transport_capacity, temperature):
    """
    function computing the initial cost of district heating

    :param length: length of district heating connection in km.
    :type length: float.
    :param transport_capacity: desired heat transport capacity in kW.
    :type transport_capacity: float.
    :param temperature: temperature of the heat transferred through the pipe in °C.
    :type temperature: float.
    :return: initial cost to set up the district heating in €.
    :rtype: float.
    """

    c = 200
    return length * np.sqrt(transport_capacity) * c


def district_heating_operational_costs(length, transport_capacity, temperature):
    """
    function computing the running cost of district heating

    :param length: length of district heating connection in km.
    :type length: float.
    :param transport_capacity: desired heat transport capacity in kW.
    :type transport_capacity: float.
    :param temperature: temperature of the heat transferred through the pipe in °C.
    :type temperature: float.
    :return: running cost of the district heating in €.
    :rtype: float.
    """

    c = 1
    return length * np.sqrt(transport_capacity)  * c


def normalize(vector):
    return vector/np.linalg.norm(vector)


def angle_between_connections(coordinate_11, coordinate_12, coordinate_21, coordinate_22):
    coordinate_11 = np.array(coordinate_11)
    coordinate_12 = np.array(coordinate_12)
    coordinate_21 = np.array(coordinate_21)
    coordinate_22 = np.array(coordinate_22)
    line_1 = coordinate_12 - coordinate_11
    line_2 = coordinate_22 - coordinate_21
    angle = np.degrees(np.arccos(np.clip(np.dot(normalize(line_1), normalize(line_2)), -1, 1)))
    return angle




