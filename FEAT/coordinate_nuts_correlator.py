import os
import csv

import re
import fiona
import pandas as pd
from shapely.geometry import Point, shape


def coordinate_nuts_correlator(file, geom_header, nuts_level, tolerance=0.02, complete=False):
    """
    function correlating nuts ID's to sites.

    :param file: absolute path of the csv file
    :type file: string.
    :param geom_header: header of the column containing the geom strings of the form SRID=4326;POINT(lon lat).
    :type geom_header: string.
    :param nuts_level: type of nuts id to correlate.
    :type nuts_level: integer; only {0, 2} accepted.
    :param complete: if True recomputes nuts id even if the nuts id is already found in the csv file.
    :type complete; Bool.
    :param tolerance: the amount of increase in size of polygons in degrees, if no direct match was found
    :return: none, replaces csv file
    """
    with open(file, 'r') as csv_file:
        delimiter = csv.Sniffer().sniff(csv_file.readline()).delimiter

    sites = pd.read_csv(file, sep=delimiter)

    # navigate to proper shapefile
    sub_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sub_path = os.path.dirname(sub_path)
    sub_path = os.path.join(sub_path, "data")
    if nuts_level is 3:
        sub_path = os.path.join(sub_path, "Nuts_3")
        sub_path = os.path.join(sub_path, "NUTS_RG_01M_2013_4326_LEVL_3.shp")
    elif nuts_level is 2:
        sub_path = os.path.join(sub_path, "Nuts_2")
        sub_path = os.path.join(sub_path, "NUTS_RG_01M_2013_4326_LEVL_2.shp")
    elif nuts_level is 1:
        sub_path = os.path.join(sub_path, "Nuts_1")
        sub_path = os.path.join(sub_path, "NUTS_RG_01M_2013_4326_LEVL_1.shp")
    elif nuts_level is 0:
        sub_path = os.path.join(sub_path, "Nuts_0")
        sub_path = os.path.join(sub_path, "NUTS_RG_01M_2013_4326_LEVL_0.shp")
    else:
        raise ValueError("Nuts level must be an integer between 0-3")

    # build shapely shapes out of shapefile
    polygons = []
    with fiona.open(sub_path, "r") as nuts_tiles:
        for nuts_tile in nuts_tiles:
            g = nuts_tile["geometry"]
            g = shape(g)
            name = nuts_tile["properties"]["NUTS_ID"]
            polygons.append([g, name])
    if "Nuts" + str(nuts_level)+"_ID" not in sites.columns.values.tolist():
        sites["Nuts" + str(nuts_level) + "_ID"] = ""

    # check in which polygon the points are located
    nuts_ids = []
    for _, site in sites.iterrows():
        if complete is False and site["Nuts" + str(nuts_level)+"_ID"] != "":
            nuts_ids.append(site["Nuts" + str(nuts_level)+"_ID"])
        else:
            if not pd.isna(site["geom"]):
                ellipsoid, coordinate = site[geom_header].split(";")
                m = re.search("[-+]?[0-9]*\.?[0-9]+.[-+]?[0-9]*\.?[0-9]+", coordinate)
                m = m.group(0)
                lon, lat = m.split(" ")
                lon = float(lon)
                lat = float(lat)
                point = Point((lon, lat))
                contains = False
                for polygon in polygons:
                    if polygon[0].contains(point):  # check if shape of polygon contains point
                        nuts_ids.append(polygon[1])  # append name of polygon
                        contains = True
                        break
                if contains is False:
                    for polygon in polygons:
                        if polygon[0].buffer(tolerance).contains(point):  # check if shape of polygon contains point with margins
                            nuts_ids.append(polygon[1])  # append name of polygon
                            contains = True
                            break
                if contains is False:
                    nuts_ids.append("")  # if no polygon containing the point was found
            else:
                nuts_ids.append("")

    sites["Nuts" + str(nuts_level) + "_ID"] = nuts_ids
    sites.to_csv(file, sep=delimiter, index=False)
    return


if __name__ == "__main__":
    path = os.path.dirname(
           os.path.dirname(
           os.path.dirname(os.path.abspath(__file__))))
    path = os.path.join(os.path.join(path, "data"), "Bedarfe(EPER-35-30er).csv")
    coordinate_nuts_correlator(path, "geom", 3, complete=True)
