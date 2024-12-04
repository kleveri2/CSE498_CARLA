# depreciated

# import osmnx as ox
# from matplotlib import pyplot as plt
# from shapely.geometry import Point
# from tqdm import tqdm
# import overpass
# from pyproj import Transformer
# import networkx as nx
#
# def latlon_to_unreal_coords(lat, lon, origin_lat, origin_lon):
#     transformer = Transformer.from_crs("epsg:4326", "epsg:3857", always_xy=True)
#     origin_x, origin_y = transformer.transform(origin_lon, origin_lat)
#     x, y = transformer.transform(lon, lat)
#     ue_x = x - origin_x
#     ue_y = y - origin_y
#     ue_z = 0
#     return ue_x, ue_y, ue_z
#
# def plot_map_with_signs(G, stops):
#     fig, ax = ox.plot_graph(G, show=False, close=False, node_size=0, edge_color='gray')
#
#     sign_x = [sign['location'][0] for sign in stops]
#     sign_y = [sign['location'][1] for sign in stops]
#
#     sign_types = {}
#     for sign in stops:
#         sign_type = sign['type']
#         x, y = sign['location']
#         if sign_type not in sign_types:
#             sign_types[sign_type] = {'x': [], 'y': []}
#         sign_types[sign_type]['x'].append(x)
#         sign_types[sign_type]['y'].append(y)
#
#     # Define markers and colors for different sign types
#     marker_styles = {
#         'stop_sign': {'color': 'red', 'marker': '^', 'label': 'Stop Sign'},
#         # 'yield_sign': {'color': 'blue', 'marker': 's', 'label': 'Yield Sign'},
#         # 'speed_limit': {'color': 'green', 'marker': 'o', 'label': 'Speed Limit Sign'},
#         # Add more sign types as needed
#     }
#
#     # Plot each sign type
#     for sign_type, coords in sign_types.items():
#         style = marker_styles.get(sign_type, {'color': 'black', 'marker': 'x', 'label': sign_type})
#         ax.scatter(coords['x'], coords['y'], c=style['color'], marker=style['marker'], s=50, label=style['label'])
#
#     # Add legend
#     ax.legend()
#
#     # Display the plot
#     plt.show()
#
# def generate_synthetic_signs(G):
#     def is_major_road(road_type):
#         return road_type in ['motorway', 'trunk', 'primary', 'secondary']
#
#     def is_minor_road(road_type):
#         return road_type in ['tertiary', 'residential', 'service']
#
#     def has_traffic_signal(node):
#         return 'traffic_signal' in G.nodes[node].get('highway', '')
#
#     synthetic_signs = []
#     for node in G.nodes():
#         if G.degree(node) > 2:
#             if has_traffic_signal(node):
#                 continue  # Skip nodes with traffic signals
#
#             connected_edges = G.edges(node, keys=True, data=True)
#             road_types = {}
#
#             for u, v, key, data in connected_edges:
#                 highway = data.get('highway', '')
#                 if isinstance(highway, list):
#                     highway = highway[0]
#                 road_types[(u, v)] = highway
#
#             major_road_present = any(is_major_road(rt) for rt in road_types.values())
#             minor_road_present = any(is_minor_road(rt) for rt in road_types.values())
#
#             if not major_road_present and minor_road_present:
#                 for (u, v), rt in road_types.items():
#                     if is_minor_road(rt):
#                         # Determine orientation
#                         start_point = (G.nodes[u]['x'], G.nodes[u]['y'])
#                         end_point = (G.nodes[v]['x'], G.nodes[v]['y'])
#                         # bearing = calculate_bearing(start_point, end_point)
#                         synthetic_signs.append({
#                             'location': start_point,
#                             'type': 'stop_sign',
#                             # 'orientation': bearing
#                         })
#     plot_map_with_signs(G, synthetic_signs)
#     return synthetic_signs
#
#
# def main():
#     south, west, north, east = 42.686306, -84.508982, 42.687652, -84.505822
#     # Add_Signs(north, south, east, west)
#
# if __name__ == "__main__":
#     main()