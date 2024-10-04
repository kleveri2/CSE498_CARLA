import osmnx as ox
from matplotlib import pyplot as plt
from shapely.geometry import Point
from tqdm import tqdm
def apply_sign_nodes(G, stop_tag, speed_tag, yield_tag):
    stop_locations = []
    speed_locations = []
    yield_locations = []

    for u, v, key, data in tqdm(G.edges(keys=True, data=True), total=len(G.edges())):
        road_geom = data.get('geometry', None)
        if road_geom:
            stop_location = Point(road_geom.coords[0])
            stop_locations.append((stop_location.x, stop_location.y))

            mindex = len(road_geom.coords) // 2
            speed_location = Point(road_geom.coords[mindex])
            speed_locations.append((speed_location.x, speed_location.y))

            yield_location = Point(road_geom.coords[-1])
            yield_locations.append((yield_location.x, yield_location.y))
    return stop_locations, speed_locations, yield_locations

def plot_map_with_signs(G, stops, limits, yields):
    fig, ax = ox.plot_graph(G, show=False, close=False, dpi=200)

    for x, y in stops:
        ax.plot(x, y, 'ro', markersize=2, label='Stop Sign')

    for x, y in limits:
        ax.plot(x, y, 'bo', markersize=2, label='Speed Limit Sign')

    for x, y in yields:
        ax.plot(x, y, 'go', markersize=2, label='Yield Sign')

    plt.title('Road Network with Sign Locations')
    plt.show()

def Add_Signs(G):
    print("Adding Signs to road network")

    #usable signs: https://wiki.openstreetmap.org/wiki/Key:traffic_sign
    stop_tag = 'stop'
    speed_tag = 'speed_limit'
    yield_tag = 'yield'

    stops, limits, yields = apply_sign_nodes(G, stop_tag, speed_tag, yield_tag)
    plot_map_with_signs(G, stops, limits, yields)