#code found at https://github.com/JHMeusener/osm2xodr
#changes were made to work with our real world elevation function

from math import floor, pi
import numpy as np
import argparse
import requests
import os
import xml.etree.ElementTree as ET
from OSMParser.testing import TestEntity, _test_nodes, testSimpleRoad, test_3WayTCrossing2
from OSMParser.osmParsing import parseAll,rNode, OSMWay,JunctionRoad, OSMWayEndcap, createOSMJunctionRoadLine, createOSMWayNodeList2XODRRoadLine
from OSMParser.xodrWriting import startBasicXODRFile,fillNormalRoads,fillJunctionRoads

# Hard-coded API key and paths
#C:\Users\jakin\Downloads\osm2xodr-master\osm2xodr-master
API_KEY = "d54b0fdd6de0f7a46aa17d4a0a9b8624"
#XODR_OUTPUT_PATH = "C:\\Users\\jakin\\Downloads\\osm2xodr-master\\osm2xodr-master\\output6.xodr"
#TOPO_MAP_PATH = "C:\\Users\\jakin\\Downloads\\osm2xodr-master\\osm2xodr-master\\topomap.png"

def OpenTopographyDownload(south, north, west, east, output_file, api_key, demtype="NASADEM"):
    url = "https://portal.opentopography.org/API/globaldem"
    params = {
        "demtype": demtype,
        "south": south,
        "north": north,
        "west": west,
        "east": east,
        "outputFormat": "GTiff",
        "API_Key": api_key
    }
    response = requests.get(url, params=params, stream=True)
    if response.status_code == 200:
        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"Elevation data saved to {output_file}")
    else:
        print("Failed to download elevation data:", response.text)
        response.raise_for_status()

def Get_Coords(osm_file):
    tree = ET.parse(osm_file)
    root = tree.getroot()
    bounds = root.find("bounds")
    if bounds is not None:
        south = float(bounds.get("minlat"))
        north = float(bounds.get("maxlat"))
        west = float(bounds.get("minlon"))
        east = float(bounds.get("maxlon"))
        print("south: ", south)
        print("north: ", north)
        print("west: ", west)
        print("east: ", east)
        return south, north, west, east
    else:
        raise ValueError("No Coordinates found")

def main():
    parser = argparse.ArgumentParser(description="Convert OSM to XODR with elevation data from OpenTopography.")
    parser.add_argument("osm_file", type=str, help="Path to the input OSM file.")
    parser.add_argument("xodr_output_path", type=str, help="Path to save the output XODR file.")
    parser.add_argument("topo_map_path", type=str, help="Path to save the downloaded topographic map.")
    args = parser.parse_args()

    # Coordinates
    south, north, west, east = Get_Coords(args.osm_file)

    OpenTopographyDownload(south, north, west, east, args.topo_map_path, API_KEY)

    parseAll(args.osm_file, bildpfad=args.topo_map_path, minimumHeight=163.0, maximumHeight=192.0, curveRadius=12)

    startBasicXODRFile(args.xodr_output_path)
    fillNormalRoads(args.xodr_output_path)
    fillJunctionRoads(args.xodr_output_path)

    print(f"XODR file saved at {args.xodr_output_path}")

if __name__ == "__main__":
    main()