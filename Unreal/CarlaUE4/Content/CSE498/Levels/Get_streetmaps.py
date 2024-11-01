import osmnx as ox
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point, box
import random
import numpy as np

print("hi")
place_name = "Edgewood Washington, DC, USA"
area = ox.geocode_to_gdf(place_name)
type(area)
area.plot()
plt.show()

tags = {'highway': True}
buildings = ox.features_from_place(place_name, tags)
buildings.head()
buildings.plot()
plt.show()


# Retrieve the road network graph.
G = ox.graph_from_place(place_name, network_type='drive')
nodes, edges = ox.graph_to_gdfs(G)
edges_projected = edges.to_crs(epsg=3857)  # Web Mercator projection

# Calculate the length of each road segment and add them together, then convert to km.
edges_projected['length_m'] = edges_projected.geometry.length
total_road_length_m = edges_projected['length_m'].sum()
total_road_length_km = total_road_length_m / 1000

print(f"Total road length: {total_road_length_km:.2f} km")

# Retrieve the area boundary as a GeoDataFrame
area = ox.geocode_to_gdf(place_name)

# Project the area GeoDataFrame to the same CRS as the edges
area_projected = area.to_crs(epsg=3857)

# Calculate the area in square meters
area_projected['area_m2'] = area_projected.geometry.area

# Extract the area value and convert the area to square kilometers.
area_m2 = area_projected['area_m2'].iloc[0]
area_km2 = area_m2 / 1e6

print(f"Area of the region: {area_km2:.2f} km²")

# Compute road density (km of road per km²)
road_density = total_road_length_km / area_km2

print(f"Road density: {road_density:.2f} km/km²")

