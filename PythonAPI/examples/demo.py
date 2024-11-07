
import os
import random
import sys
import glob
import time

from types import LambdaType
from collections import deque
from collections import namedtuple

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass
import carla


sys.path.append('C:\CSE498_CARLA\PythonAPI\carla')

def modify_vehicle_physics(vehicle):
    try:
        physics_control = vehicle.get_physics_control()
        physics_control.use_sweep_wheel_collision = True
        vehicle.apply_physics_control(physics_control)
    except Exception as e:
        print(f"Failed to modify vehicle physics: {e}")

def main():
    actor_list  = []
    sensor_list = []

    try:
        client = carla.Client('localhost', 2000)
        client.set_timeout(5.0)
        world = client.get_world()
        blueprint_library = world.get_blueprint_library()

        vehicle_bp = blueprint_library.find('vehicle.mercedes.coupe')
        spawn_points = world.get_map().get_spawn_points()
        transform = random.choice(spawn_points)
        transform.location.z += 1.0
        transform.rotation.roll = 0.0
        transform.rotation.pitch = 0.0
        vehicle = world.try_spawn_actor(vehicle_bp, transform)
        attempts = 0
        max_attempts = 10

        while vehicle is None and attempts < max_attempts:
            print(f"Spawn attempt {attempts + 1} failed due to collision. Trying a new location...")
            transform = random.choice(spawn_points)
            waypoint = world.get_map().get_waypoint(transform.location, project_to_road=True, lane_type=carla.LaneType.Driving)
            transform = waypoint.transform
            transform.location.z += 1.0
            transform.rotation.roll = 0.0
            transform.rotation.pitch = 0.0
            vehicle = world.try_spawn_actor(vehicle_bp, transform)
            attempts += 1

        if vehicle is None:
            raise RuntimeError("Failed to spawn vehicle after multiple attempts")

        # 启用轮胎碰撞检测
        modify_vehicle_physics(vehicle)

        # 设置车辆自动驾驶
        #vehicle.set_autopilot(True)

        target_transform = world.get_map().get_spawn_points()[20]

        from agents.navigation.basic_agent import BasicAgent
        agent = BasicAgent(vehicle)

        destination = target_transform.location
        agent.set_destination(destination)



        
        while True:
            spectator = world.get_spectator()
            transform = vehicle.get_transform()
            spectator.set_transform(carla.Transform(vehicle.get_transform().transform(carla.Location(x=-10,z=2)),vehicle.get_transform().rotation))

            if agent.done():
                print("The target has been reached, stopping the simulation")
                
                break
            control=agent.run_step()
            vehicle.apply_control(control)
        vehicle.destroy()
        #actor_list.remove(vehicle)


    finally:
        client.apply_batch([carla.command.DestroyActor(x) for x in actor_list])
        for sensor in sensor_list:
            sensor.destroy()
        print('done')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('user exit')