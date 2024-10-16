import glob
import os
import sys
import carla

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

def set_dark_rainy_weather(world):
    weather = carla.WeatherParameters(
        cloudiness=100.0,  # 云量
        precipitation=100.0,  # 降水量
        precipitation_deposits=100.0,  # 降水沉积
        wind_intensity=50.0,  # 风强度
        sun_azimuth_angle=0.0,  # 太阳方位角
        sun_altitude_angle=-90.0  # 太阳高度角，负值表示黑夜
    )
    world.set_weather(weather)

def main():
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)

    world = client.get_world()

    # 设置黑夜下雨的天气条件
    set_dark_rainy_weather(world)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(' - Exited by user.')