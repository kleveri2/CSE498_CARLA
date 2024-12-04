import os
import shutil

import osmnx as ox
import matplotlib.pyplot as plt
import requests
from geopy.distance import geodesic
from geopy import Point
import random
import warnings
# import Add_Signs
import Add_Signs_Mapillary
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import json

# used to clear space clutter after searching many locations
def clear_osmnx_cache():
    cache_dir = ox.settings.cache_folder
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
        print(f"OSMnx cache at '{cache_dir}' has been cleared.")
    else:
        print(f"No OSMnx cache directory found at '{cache_dir}'.")

# used in various places for mathmatical interpolations
def bounding_box(lat, lon, side_km):
    center = Point(lat, lon)
    d = side_km / 2.0
    north = geodesic(kilometers=d).destination(center, bearing=0)
    south = geodesic(kilometers=d).destination(center, bearing=180)
    east = geodesic(kilometers=d).destination(center, bearing=90)
    west = geodesic(kilometers=d).destination(center, bearing=270)
    return north.latitude, south.latitude, east.longitude, west.longitude

# checks qualifications of area, density, feature prescence, etc
def try_location(lat_lon_tuple, road_density, area_in_km, acceptable_range, min_feature_ratio, stop_event):
    # Check if another thread has found a location
    if stop_event.is_set():
        return None

    lat, lon = lat_lon_tuple
    side_km = area_in_km ** 0.5
    min_road_den = road_density * (1 - acceptable_range)
    max_road_den = road_density * (1 + acceptable_range)

    north_lat, south_lat, east_lon, west_lon = bounding_box(lat, lon, side_km)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=FutureWarning)
        try:
            bbox = (north_lat, south_lat, east_lon, west_lon)
            G = ox.graph_from_bbox(*bbox, network_type='drive', simplify=True)
            if G is None or len(G.nodes) == 0:
                raise ValueError("No graph data")
            total_len = ox.stats.edge_length_total(G) / 1000  # Convert to km
            current_road_density = total_len / area_in_km
            if min_road_den <= current_road_density <= max_road_den:
                # Fetch map features (e.g., stop signs)
                # signs = Add_Signs_Mapillary.main(west_lon, south_lat, east_lon, north_lat)
                signs = Add_Signs_Mapillary.fetch_features(south_lat, west_lon, north_lat, east_lon)
                # Calculate min_features as a percentage of nodes
                min_features = len(G.nodes) * min_feature_ratio
                # if len(signs) >= min_features:
                if len(signs) >= 1:
                    print(f"Location found at ({lat}, {lon}) with sufficient map features.")
                    # Signal other threads to stop
                    # stop_event.set()
                    return lat, lon, current_road_density, G, signs
                else:
                    print(f"Not enough features found ({len(signs)} features) at ({lat}, {lon}). Required: {min_features:.2f} features. Continuing search.")
                    # return None
            else:
                print(f"Road density {current_road_density:.2f} km/km^2 not within acceptable range at ({lat}, {lon}).")
                # return None
        except ValueError as ve:
            print(f"Error: {ve} at ({lat}, {lon})")
            # return None
        except Exception as e:
            print(f"Exception: {e} at ({lat}, {lon})")
            # return None

# finds a random location based on min/max lat/long.
def find_locations(road_density, area_in_km):
    max_workers = 10
    min_feature_ratio = 0.1
    acceptable_range = 0.5  # 50% tolerance
    # Search map bounds (e.g., northeastern USA)
    min_lat, max_lat = 35.0, 45.0
    min_lon, max_lon = -95.0, -75.0

    # test setting
    # min_lat, max_lat = 35.90028568262687, 35.90929816373677
    # min_lon, max_lon = -78.59981000128799, -78.58873236174334

    lat_lon_list = [(random.uniform(min_lat, max_lat), random.uniform(min_lon, max_lon)) for _ in range(10000)]

    found_location = None
    stop_event = threading.Event()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                try_location, lat_lon, road_density, area_in_km, acceptable_range, min_feature_ratio, stop_event
            ): lat_lon for lat_lon in lat_lon_list
        }
        for future in as_completed(futures):
            result = future.result()
            if result:
                found_location = result
                # Signal the stop_event to stop other threads
                stop_event.set()
                for f in futures:
                    f.cancel()
                print("Suitable location found. Exiting search.")
                break  # Exit the loop as we found a suitable location
    return found_location

# used for testing
def plot_road(G):
    fig, ax = ox.plot_graph(G, show=False, close=False)
    plt.title('Road Network of Found Location')
    plt.show()
# collects coordinates of all signs in  area
def plot_signs(G, signs):
    # Plot the graph without projecting it (coordinates remain in lat/lon)
    fig, ax = ox.plot_graph(
        G,
        show=False,
        close=False,
        dpi=200,
        node_size=0,
        edge_color='gray',
        edge_linewidth=0.5,
        bgcolor='white'
    )

    # Extract longitude and latitude from the signs data
    signs_coords = [
        (feature['geometry']['coordinates'][0], feature['geometry']['coordinates'][1])
        for feature in signs
    ]
    # print(signs_coords)

    # Unzip the coordinates into separate lists
    lons, lats = zip(*signs_coords) if signs_coords else ([], [])

    # Plot the signs on the map
    ax.scatter(lons, lats, s=30, c='red', marker='o', label='Stop Sign', zorder=5)

    plt.title('Road Network with Sign Locations')
    plt.legend()
    # plt.show()
    return signs_coords

# the "main function" for Find_By_Density
def find(road_density=20, area_in_km=5):
    found_location = find_locations(road_density, area_in_km)
    if found_location:
        lat, lon, road_density, G, signs = found_location
        side_km = area_in_km ** 0.5
        north_lat, south_lat, east_lon, west_lon = bounding_box(lat, lon, side_km)
        print("Plotting Map")
        # plot_road(G)
        if len(signs) > 0:
            coords = plot_signs(G, signs)
        else:
            print("No stop signs found.")
            coords = None
        print("fetching map")
        overpass_url = "http://overpass-api.de/api/map?bbox="
        search = str(west_lon) + "," + str(south_lat) + "," + str(east_lon) + "," + str(north_lat)
        print(overpass_url + search)
        # response = requests.get(overpass_url + search)
        # print("Location found")

        delta_lat = north_lat - south_lat
        delta_lon = east_lon - west_lon
        delta_UE4x = area_in_km
        delta_UE4y = -area_in_km
        scale_x = (delta_UE4x / delta_lon) * 100000
        scale_y = (delta_UE4y / delta_lat) * 100000
        # print(scale_x)
        # print(scale_y)

        if coords:
            x_coords, y_coords = zip(*coords)
            new_coords_x = []
            new_coords_y = []
            for val in x_coords:
                adjusted_val = (float(val)-west_lon) * scale_x
                new_coords_x.append(adjusted_val)
            for val in y_coords:
                adjusted_val = (float(val)-south_lat) * scale_y
                new_coords_y.append(adjusted_val)
            # print(type(new_coords_x[0]))
            # print(new_coords_x)
        else:
            new_coords_x = new_coords_y = []
        clear_osmnx_cache()
        # yield overpass_url + search
        with open('C:/CSE498_CARLA/Unreal/CarlaUE4/Content/CSE498/Levels/Prep_Maps/x.json', 'w') as file:
            json.dump(new_coords_x, file)
        with open('C:/CSE498_CARLA/Unreal/CarlaUE4/Content/CSE498/Levels/Prep_Maps/y.json', 'w') as file:
            json.dump(new_coords_y, file)
        return overpass_url + search, new_coords_x, new_coords_y
    else:
        print("No suitable location found.")
        clear_osmnx_cache()
        return None

def main():
    # line = input("Enter density and area: \n").split()
    # nv = find(int(line[0]), int(line[1]))
    nv, x, y = find()
    print(x)

if __name__ == "__main__":
    main()
