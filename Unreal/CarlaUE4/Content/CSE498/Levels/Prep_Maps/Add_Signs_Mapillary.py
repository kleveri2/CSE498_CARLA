import requests, json, mercantile
from pyproj import Proj, Transformer

# Mapillary access token -- provide your own, replace this example
mly_key = 'MLY|8567666719993755|2b50c7e210332948405be7a5d6533ccc'
STOPS_LIST = ['regulatory--stop--g10', 'regulatory--stop--g1', 'regulatory--stop--g2', 'regulatory--stop--g3',
              'regulatory--stop--g4', 'regulatory--stop--g5', 'regulatory--stop--g6', 'regulatory--stop--g7',
              'regulatory--stop--g8', 'regulatory--stop--g9']

def fetch_features(south, west, north, east):
    # use zoom 18 size map tiles, which are quite small -- see https://mapsam.com/map to understand the sizes
    # tiles = list(mercantile.tiles(east, south, west, north, 1))
    # bbox_list = [mercantile.bounds(tile.x, tile.y, tile.z) for tile in tiles]

    features = []
    # i = 0
    # loop through each smaller bbox to request data
    # for bbox in bbox_list:
    #     i += 1
    bbox_features = []
# bbox_str = str(f'{bbox.west},{bbox.south},{bbox.east},{bbox.north}')
    bbox_str = str(f'{west},{south},{east},{north}')
    # url = f'https://graph.mapillary.com/map_features?access_token={mly_key}&fields=id,object_value,geometry&bbox={bbox_str}'

    url = f'https://graph.mapillary.com/map_features?access_token={mly_key}&fields=id,object_value,geometry&bbox={bbox_str}&layers=traffic_signs'
    response = requests.get(url)
    if response.status_code == 200:
        # print(url)
        # print(i)
        # print("connection established")
        json = response.json()

        # check if the response is empty or not
        if len(json['data']):
            for obj in json['data']:
                # build a GeoJSON object for each feature
                feature = {}
                feature['type'] = 'Feature'
                feature['properties'] = {}
                feature['geometry'] = obj['geometry']
                feature['properties']['id'] = obj['id']
                feature['properties']['object_value'] = obj['object_value']
                if obj['object_value'] in STOPS_LIST:
                    # merge into the list of all feature objects
                    bbox_features.append(feature)
                    features += bbox_features
    else:
        print("Failed to connect: ", response.status_code)
    return features

# def Convert_Coordinates(features):
#
#     return 0


def main():
    south, west, north, east = 42.686641, -84.514416, 42.688082, -84.511449
    features = fetch_features(south, west, north, east)
    print(features)


if __name__ == "__main__":
    main()