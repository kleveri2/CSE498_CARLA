import osmnx as ox
import matplotlib.pyplot as plt
import requests
from geopy.distance import geodesic
from geopy import Point
import random
import warnings
# import Add_Signs

import Add_Signs_Mapillary
def bounding_box(lat, lon, side_km):
    center = Point(lat, lon)
    d = side_km / 2.0
    north = geodesic(kilometers=d).destination(center, bearing=0)
    south = geodesic(kilometers=d).destination(center, bearing=180)
    east = geodesic(kilometers=d).destination(center, bearing=90)
    west = geodesic(kilometers=d).destination(center, bearing=270)
    return north.latitude, south.latitude, east.longitude, west.longitude
def find_locations(road_density, area_in_km, max_retries=5, min_feature_ratio=0.1):
    side_km = area_in_km ** 0.5
    acceptable_range = 0.5  # 50% tolerance
    min_road_den = road_density * (1 - acceptable_range)
    max_road_den = road_density * (1 + acceptable_range)
    # Search map bounds (e.g., northeastern USA)
    min_lat, max_lat = 35.0, 45.0
    min_lon, max_lon = -95.0, -75.0

    while True:
        for attempt in range(max_retries):
            lat = random.uniform(min_lat, max_lat)
            lon = random.uniform(min_lon, max_lon)
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
                        signs = Add_Signs_Mapillary.fetch_features(south_lat, west_lon, north_lat, east_lon)
                        # Calculate min_features as a percentage of nodes
                        min_features = len(G.nodes) * min_feature_ratio
                        if len(signs) >= min_features:
                            print("Location found with sufficient map features.")
                            return lat, lon, current_road_density, G, signs
                        else:
                            print(f"Not enough features found ({len(signs)} features). Required: {min_features:.2f} features. Continuing search.")
                            continue
                except ValueError as ve:
                    print(f"Error: {ve}")
                    continue
                except Exception as e:
                    print(f"Exception: {e}")
                    continue
def plot_road(G):
    fig, ax = ox.plot_graph(G, show=False, close=False)
    plt.title('Road Network of Found Location')
    plt.show()

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

def find(road_density=20, area_in_km=1):
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
        response = requests.get(overpass_url + search)
        print("Location found")
        x_coords, y_coords = zip(*coords)
        new_coords_x = []
        new_coords_y = []
        for val in x_coords:
            new_coords_x.append(float(val))
        for val in y_coords:
            new_coords_y.append(float(val))
        # print(type(new_coords_x[0]))
        return overpass_url + search, new_coords_x, new_coords_y
    else:
        print("No suitable location found.")

def main():
    nv = find(15, 5)

if __name__ == "__main__":
    main()