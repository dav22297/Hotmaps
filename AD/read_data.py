
__author__ = "David Schilling"

import pandas as pd
import os
import csv
import re


def ad_industrial_database():
    """
    loads data of heat sources given by a csv file.

    :return: dataframe containing the data of the csv file.
    :rtype: pandas dataframe.
    """

    # TODO variable file name?
    path = os.path.dirname(
           os.path.dirname(
           os.path.dirname(os.path.abspath(__file__))))
    path = os.path.join(os.path.join(path, "data"), "Industrial_Database_reduced.csv")

    # determine delimiter of csv file
    with open(path, 'r') as csv_file:
        delimiter = csv.Sniffer().sniff(csv_file.readline()).delimiter

    # TODO encoding standard; maybe agree on delimiter
    raw_data = pd.read_csv(path, sep=delimiter, usecols=("geom", "Subsector", "Excess_Heat_100-200C",
                                                        "Excess_Heat_200-500C", "Excess_Heat_500C", "Nuts0_ID"))

    # dataframe for processed data
    data = pd.DataFrame(columns=("ellipsoid", "Lon", "Lat", "Nuts0_ID", "Subsector", "Excess_heat", "Temperature"))
    for i, site in raw_data.iterrows():
        # check if site location is available
        if not pd.isna(site["geom"]):
            # extract ellipsoid model and (lon, lat) from the "geom" column
            ellipsoid, coordinate = site["geom"].split(";")
            m = re.search("[-+]?[0-9]*\.?[0-9]+.[-+]?[0-9]*\.?[0-9]+", coordinate)
            m = m.group(0)
            lon, lat = m.split(" ")
            lon = float(lon)
            lat = float(lat)

            # check if heat at specific temperature range is available
            # TODO deal with units; hard coded temp ranges?
            if not pd.isna(site["Excess_Heat_100-200C"]):
                data.loc[data.shape[0]] = (ellipsoid, lon, lat, site["Nuts0_ID"], site["Subsector"],
                                           site["Excess_Heat_100-200C"], 150)
            if not pd.isna(site["Excess_Heat_200-500C"]):
                data.loc[data.shape[0]] = (ellipsoid, lon, lat, site["Nuts0_ID"],
                                           site["Subsector"], site["Excess_Heat_200-500C"], 350)
            if not pd.isna(site["Excess_Heat_500C"]):
                data.loc[data.shape[0]] = (ellipsoid, lon, lat, site["Nuts0_ID"],
                                           site["Subsector"], site["Excess_Heat_500C"], 500)

    return data


def ad_eper_35_30():
    """
    loads data of heat sinks given by a csv file.

    :return: dataframe containing the data of the csv file.
    :rtype: pandas dataframe.
    """

    # TODO variable file name?
    path = os.path.dirname(
           os.path.dirname(
           os.path.dirname(os.path.abspath(__file__))))
    path = os.path.join(os.path.join(path, "data"), "Bedarfe(EPER-35-30er)_reduced.csv")
    # determine delimiter of csv file
    with open(path, 'r') as csv_file:
        delimiter = csv.Sniffer().sniff(csv_file.readline()).delimiter

    # TODO encoding standard, maybe agree on delimiter
    raw_data = pd.read_csv(path, sep=delimiter, usecols=("geom", "NACEMainEconomicActivityName", "Heat demand [TWh]",
                                                         "Temperatur - Bedarf [C]", "Nuts2_ID"))

    # dataframe for processed data
    data = pd.DataFrame(columns=("ellipsoid", "Lon", "Lat","Nuts2_ID", "Economic_Activity", "Heat_demand",
                                 "Temperature"))
    for i, site in raw_data.iterrows():
        # check if site location is available
        if not pd.isna(site["geom"]):
            # extract ellipsoid model and (lon, lat) from the "geom" column
            ellipsoid, coordinate = site["geom"].split(";")
            m = re.search("[-+]?[0-9]*\.?[0-9]+.[-+]?[0-9]*\.?[0-9]+", coordinate)
            m = m.group(0)
            lon, lat = m.split(" ")
            lon = float(lon)
            lat = float(lat)

            # add heat_sink as new entry
            # TODO deal with units
            data.loc[data.shape[0]] = (ellipsoid, lon, lat, site["Nuts2_ID"], site["NACEMainEconomicActivityName"],
                                       site["Heat demand [TWh]"], site["Temperatur - Bedarf [C]"])

    return data


def ad_industry_profiles():
    """
    loads industry profiles of different subcategories from different csv files.

    :return: list of dataframes containing the csv files data.
    :rtype: list [pd.Dataframe, pd.Dataframe, ...].
    """

    # folder and files names of csv files
    # TODO variable file name?
    folder_names = ("load_profile_industry_chemicals_and_petrochemicals_yearlong_2018-master",
                    "load_profile_industry_food_and_tobacco_yearlong_2018-master",
                    "load_profile_industry_iron_and_steel_yearlong_2018-master",
                    "load_profile_industry_non_metalic_minerals_yearlong_2018-master",
                    "load_profile_industry_paper_yearlong_2018-master")
    file_names = ("hotmaps_task_2.7_load_profile_industry_chemicals_and_petrochemicals_yearlong_2018.csv",
                  "hotmaps_task_2.7_load_profile_industry_food_and_tobacco_yearlong_2018.csv",
                  "hotmaps_task_2.7_load_profile_industry_iron_and_steel_yearlong_2018.csv",
                  "hotmaps_task_2.7_load_profile_industry_non_metalic_minerals_yearlong_2018.csv",
                  "hotmaps_task_2.7_load_profile_industry_paper_yearlong_2018.csv")

    path = os.path.dirname(
           os.path.dirname(
           os.path.dirname(os.path.abspath(__file__))))
    path = os.path.join(path, "data")

    data = []
    for folder_name, file_name in zip(folder_names, file_names):
        sub_path = os.path.join(path, folder_name)
        sub_path = os.path.join(sub_path, "data")
        sub_path = os.path.join(sub_path, file_name)
        # determine delimiter of csv file
        with open(sub_path, 'r') as csv_file:
            delimiter = csv.Sniffer().sniff(csv_file.readline()).delimiter
        # TODO encoding standard; maybe agree on delimiter
        raw_data = pd.read_csv(sub_path, sep=delimiter, usecols=("country", "process", "hour", "load"))
        data.append(raw_data)

    return data


def ad_residential_heating_profile():
    """
    loads residential heating profiles from csv file.

    :return: dataframe containing the data of the csv file.
    :rtype pandas dataframe.
    """

    path = os.path.dirname(
       os.path.dirname(
       os.path.dirname(os.path.abspath(__file__))))
    path = os.path.join(path, "data")
    path = os.path.join(path, "load_profile_residential_heating_yearlong_2010-master")
    path = os.path.join(path, "data")
    path = os.path.join(path, "hotmaps_task_2.7_load_profile_residential_heating_yearlong_2010.csv")

    # determine delimiter of csv file
    with open(path, 'r') as csv_file:
        delimiter = csv.Sniffer().sniff(csv_file.readline()).delimiter
    data = pd.read_csv(path, sep=delimiter, usecols=("country", "process", "hour", "load"))

    return data
