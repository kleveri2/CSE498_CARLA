import osmnx as ox
import matplotlib.pyplot as plt
import requests
from geopy.distance import geodesic
from geopy import Point
import random
import warnings
import Add_Signs
import Convert_and_Display
import subprocess

def bounding_box(lat, lon, side_km):
        center = Point(lat, lon)
        d = side_km / 2.0
        north = geodesic(kilometers=d).destination(center, bearing=0)
        south = geodesic(kilometers=d).destination(center, bearing=180)
        east = geodesic(kilometers=d).destination(center, bearing=90)
        west = geodesic(kilometers=d).destination(center, bearing=270)
        return north.latitude, south.latitude, east.longitude, west.longitude


def find_locations(road_density, area_in_km, samples = 100, max_retries = 5):
    side_km = area_in_km ** .5
    acceptable_range = .5 #50% tolerance (aka, if i put in road density of 10, it will look for near fits, between 7.5 and 12.5
    min_road_den = road_density * (1 - acceptable_range)
    max_road_den = road_density * (1 + acceptable_range)

    #search map bounds... might change these later, this should be north eastern USA
    min_lat, max_lat = 35.0, 45.0
    min_lon, max_lon = -95.0, -75.0

    for i in range(samples):
        for attempt in range(max_retries):
            lat = random.uniform(min_lat, max_lat)
            lon = random.uniform(min_lon, max_lon)
            north_lat, south_lat, east_lon, west_lon = bounding_box(lat, lon, side_km)

            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=FutureWarning)

                try:
                    bbox = (north_lat, south_lat, east_lon, west_lon)
                    G = ox.graph_from_bbox(*bbox, network_type='drive', simplify=False)

                    if G is None or len(G.nodes) == 0:
                        raise ValueError("bad")

                    total_Len = ox.stats.edge_length_total(G) / 1000 #makes it km
                    road_density = total_Len/area_in_km

                    if min_road_den <= road_density <= max_road_den:
                        print("location found")
                        return lat, lon, road_density, G

                except ValueError as ve:
                    print(f"Error1, location Skipped:: {ve}")
                    continue
                except Exception as e:
                    print(f"Error2, bad location:: {e}")
                    continue
    return None

def plot_road(G):
    fig, ax = ox.plot_graph(G, show=False, close=False)
    plt.title('Road Network of Found Location')
    plt.show()


def find(road_density, area_in_km, sample_size):
    if road_density is None:
        while True:
            # road_density_in = float(input("Enter desired road density (km/km^2): "))
            # area_in_km = float(input("Enter desired area (km^2): "))
            # sample_size = int(input("Enter number of attempts: "))
            road_density = 20
            area_in_km = 1
            sample_size = 50
            if area_in_km > 5:
                print("large areas may greatly increase loading times (2km^2 = approx 10 mintues of loading)")
                if input("Continue? (Y/N) ").lower() == "y":
                    break
            else:
                break
    else:
        road_density = float(road_density)
        area_in_km = float(area_in_km)
        sample_size = int(sample_size)
    print("Road density:", road_density)
    print("searching for qualifying road network...")
    found_location = find_locations(road_density, area_in_km, sample_size)

    if found_location:
        lat, lon, road_density, G = found_location
        print("fLatitude: {lat:.6f}, Longitude: {lon:.6f}, Road Density: {rd:.2f} km/km²")
        # plot_road(G)
        print("Adding signs to map")
        # Add_Signs.Add_Signs(G)
        side_km = area_in_km ** 0.5
        print("calculating bounding box")
        # bbox = bounding_box(lat, lon, side_km)
        north_lat, south_lat, east_lon, west_lon = bounding_box(lat, lon, side_km)
        print("fetching map")
        overpass_url = "http://overpass-api.de/api/map?bbox="
        search = str(west_lon) + "," + str(south_lat) + "," + str(east_lon) + "," + str(north_lat)
        response = requests.get(overpass_url + search)
        osm_file = 'map.osm'

        print("writing map: ", overpass_url+search)
        with open(osm_file, 'wb') as f:
            f.write(response.content)
        # print("Generate map? \n (Y/n): ")
        # if input().lower() == 'y':
        #     print("Generating map...")
        #
        #     print("Done!")
        # else:
        #     print("Exiting")
        #     exit(0)

        return overpass_url+search


        # osm_filepath = 'map.osm'
        # print("Downloading osm...")
        # Convert_and_Display.download_osm_data(north_lat, south_lat, east_lon, west_lon, osm_filepath)
        # xodr_filepath = 'map.xodr'
        # print("Here's the big one! (converting and displaying map)")
        # Convert_and_Display.Convert_and_Display(osm_filepath, xodr_filepath, bbox)
        # Convert_and_Display.Convert_and_Display(bbox)
        # ox.save_graph_xml(G, filepath="C:/CSE498_CARLA/Build/libosmscout-source/maps/map.osm")
        # subprocess.run(["./build.sh"], cwd="C:/CSE498_CARLA/Build/libosmscout-source/maps", shell=True)
    else:
        print("No location found")
        return 0


# if __name__ == "__main__":
#     main()
