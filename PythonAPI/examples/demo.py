import carla
import os
import random
import sys
import glob


try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

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
        client=carla.Client('localhost',2000)
        client.set_timeout(5.0)
        world=client.get_world()
        blueprint_library=world.get_blueprint_library()
        weather=carla.WeatherParameters(
            cloudiness=10.0,
            precipitation=10.0,

        )
        world.set_weather(weather)


        vehicle_bp=blueprint_library.find('vehicle.mercedes.coupe')
        transform=random.choice(world.get_map().get_spawn_points())
        transform.location.z += 1.0
        transform.rotation.roll = 0.0
        transform.rotation.pitch = 0.0
        vehicle=world.spawn_actor(vehicle_bp,transform)
        attempts = 0
        max_attempts = 10

        while vehicle is None and attempts < max_attempts:
            print(f"Spawn attempt {attempts + 1} failed due to collision. Trying a new location...")
            spawn_point = random.choice(transform)

            waypoint = world.get_map().get_waypoint(spawn_point.location, project_to_road=True, lane_type=carla.LaneType.Driving)
            spawn_point = waypoint.transform
            spawn_point.location.z += 1.0
            spawn_point.rotation.roll = 0.0
            spawn_point.rotation.pitch = 0.0
            vehicle = world.try_spawn_actor(vehicle_bp, spawn_point)
            attempts += 1
        # 启用轮胎碰撞检测
        if vehicle is not None:
            modify_vehicle_physics(vehicle)
        else:
            raise RuntimeError("Failed to spawn vehicle")
        vehicle.set_autopilot(True)
        actor_list.append(vehicle)

        while True:
            spectator=world.get_spectator()
            transform=vehicle.get_transform()
            spectator.set_transform(carla.Transform(transform.location+carla.Location(z=20),carla.Rotation(pitch=-90)))
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
