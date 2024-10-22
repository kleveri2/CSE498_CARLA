import osmnx as ox
from matplotlib import pyplot as plt
from shapely.geometry import Point
from tqdm import tqdm
import overpass
from pyproj import Transformer


def get_traffic_signs(bbox):
    api = overpass.API(timeout=600)
    query = f"""
    (
      node["traffic_sign"~"stop"]({bbox});
      node["highway"="stop"]({bbox});
    );
    """
    response = api.get(query)
    features = response['features']
    stop_signs = []

    for feature in features:
        geometry = feature.get('geometry', {})
        if geometry.get('type') == 'Point':
            lon, lat = geometry.get('coordinates', [None, None])
            if lat is not None and lon is not None:
                stop_signs.append((lon, lat))
    return stop_signs

def latlon_to_unreal_coords(lat, lon, origin_lat, origin_lon):
    transformer = Transformer.from_crs("epsg:4326", "epsg:3857", always_xy=True)
    origin_x, origin_y = transformer.transform(origin_lon, origin_lat)
    x, y = transformer.transform(lon, lat)
    ue_x = x - origin_x
    ue_y = y - origin_y
    ue_z = 0
    return ue_x, ue_y, ue_z

def plot_map_with_signs(G, stops):
    fig, ax = ox.plot_graph(G, show=False, close=False, dpi=200)

    for x, y in stops:
        ax.plot(x, y, 'ro', markersize=2, label='Stop Sign')

    plt.title('Road Network with Sign Locations')
    plt.show()

def Add_Signs(G, north_lat, south_lat, east_lon, west_lon):
    bbox_str = f"{south_lat},{west_lon},{north_lat},{east_lon}"

    ue_stop_locations = []

    stop_locations = get_traffic_signs(bbox_str)
    origin_lat = (north_lat + south_lat) / 2
    origin_lon = (east_lon + west_lon) / 2

    print("Adding Signs to road network")
    for lon, lat in stop_locations:
        ue_x, ue_y, ue_z = latlon_to_unreal_coords(lat, lon, origin_lat, origin_lon)
        ue_stop_locations.append((ue_x, ue_y, ue_z))

    print('UE stop locations:\n', ue_stop_locations)

    #usable signs: https://wiki.openstreetmap.org/wiki/Key:traffic_sign

def main():
    south, west, north, east = 42.686306, -84.508982, 42.687652, -84.505822
    Add_Signs(north, south, east, west)


if __name__ == "__main__":
    main()