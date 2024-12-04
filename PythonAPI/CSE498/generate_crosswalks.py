import glob
import os
import sys
import random

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

client = carla.Client('127.0.0.1', 2000)
client.set_timeout(10.0)

try:
    waypoint_spread = 2.0
    min_one_lane_distance_threshold = 5
    created_crosswalks = 0
    target_crosswalks = 100

    world = client.get_world()
    map = world.get_map()
    waypoints = map.generate_waypoints(waypoint_spread)
    blueprint_library = world.get_blueprint_library()

    bin_bp = blueprint_library.find('static.prop.bin')
    purse_bp = blueprint_library.find('static.prop.purse')
    trash_bp = blueprint_library.find('static.prop.trashcan02')

    for blueprint in blueprint_library.filter('*'):
        for attr in blueprint:
            print(attr)
        if blueprint.has_attribute('name'): 
            print(f"Blueprint ID: {blueprint.id}")

    random.shuffle(waypoints)

    one_lane_candidates = {}

    #  Carla recognizes different lanes as seperate roads. Two find one-lane roads first we check that the current lane does not have an adjacent
    #  lane with type Driving. Sidewalks are an example of a non-driving lane
    for waypoint in waypoints:
        road_id = waypoint.road_id
        if road_id in one_lane_candidates:
            continue


        if not waypoint.is_junction:
            one_lane_candidate = True
            left_lane = waypoint.get_left_lane()
            right_lane = waypoint.get_right_lane()
            # print("Current: ")
            # print(waypoint.lane_type)
            if left_lane:
                if left_lane.lane_type == carla.LaneType.Driving:
                    one_lane = False
                # print("Left: ")
                # print(left_lane.lane_type)
            if right_lane:
                if right_lane.lane_type == carla.LaneType.Driving:
                    one_lane = False
                # print("Right: ")
                # print(right_lane.lane_type)
            if one_lane_candidate:
                one_lane_candidates[road_id] = waypoint

    #  If we find a waypoint on a different road next another road we assume that this is a two-lane road
    #  This logic can be extended to identify 2+ lane roads
    two_lane_roads = []
    for waypoint in waypoints:
        road_id = waypoint.road_id
        for r_id, wp in one_lane_candidates.items():
            if road_id != r_id and waypoint.transform.location.distance(wp.transform.location) < min_one_lane_distance_threshold:
                two_lane_roads.append(r_id)
                two_lane_roads.append(road_id)

    #  We subtract the two-lane roads from our one-lane candidates to get the verified one-lane roads
    one_lane_roads = list(set(one_lane_candidates.keys()) - set(two_lane_roads))
    print(one_lane_roads)


    for waypoint in waypoints:
        road_id = waypoint.road_id
        if road_id in one_lane_roads and not waypoint.is_junction:
            if world.try_spawn_actor(trash_bp, waypoint.transform):
                # print("Spawned")
                created_crosswalks += 1
                if created_crosswalks >= target_crosswalks:
                    break
        
except Exception as e:
    print(e)