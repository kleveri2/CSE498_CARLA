import json
import sys
import unreal

name = sys.argv[0]
path = "C:\CSE498_CARLA\\Unreal\CarlaUE4\Content\CSE498\Levels\Prep_Maps\\" + name + "_x.json"
# path = "C:\CSE498_CARLA\\Unreal\CarlaUE4\Content\CSE498\Levels\Prep_Maps\\Non_x.json"

with open(path, 'r') as file:
    lis = json.load(file)

for item in lis:
    unreal.log(item)
