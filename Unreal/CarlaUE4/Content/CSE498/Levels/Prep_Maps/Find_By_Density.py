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
                    G = ox.graph_from_bbox(*bbox, network_type='drive', simplify=True)
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
                    print(f"Error2, Invalid Road Density:: {e}")
                    continue
    return None

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

    # Unzip the coordinates into separate lists
    lons, lats = zip(*signs_coords) if signs_coords else ([], [])

    # Plot the signs on the map
    ax.scatter(lons, lats, s=30, c='red', marker='o', label='Stop Sign', zorder=5)

    plt.title('Road Network with Sign Locations')
    plt.legend()
    plt.show()

def find(road_density=20, area_in_km=1, sample_size=50):
    found_location = find_locations(road_density, area_in_km, sample_size)
    if found_location:
        lat, lon, road_density, G = found_location
        # print("Plotting Map")
        plot_road(G)

        side_km = area_in_km ** 0.5
        north_lat, south_lat, east_lon, west_lon = bounding_box(lat, lon, side_km)

        print("Finding stop signs")
        # Add_Signs.Add_Signs(G, north_lat, south_lat, east_lon, west_lon)
        # signs = Add_Signs.generate_synthetic_signs(G)
        signs = Add_Signs_Mapillary.fetch_features(south_lat, west_lon, north_lat, east_lon)
        if len(signs) > 0:
            print(signs)
            plot_signs(G, signs)
        else:
            print("No Stop signs")
        print("fetching map")
        overpass_url = "http://overpass-api.de/api/map?bbox="
        search = str(west_lon) + "," + str(south_lat) + "," + str(east_lon) + "," + str(north_lat)
        print(overpass_url + search)
        response = requests.get(overpass_url + search)

        return overpass_url+search
    else:
        print("No location found")

def main():
    nv = find(15, 2, 20)

if __name__ == "__main__":
    main()