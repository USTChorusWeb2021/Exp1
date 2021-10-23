# merge_image_tags.py
# USTChorusWeb2021
# By HurryPeng & WhitieKitty

import os
import json

all_image_tags = dict()

files = os.listdir("../output/image_tags")
for filename in files:
    if ".json" not in filename or len(filename) != 13:
        continue
    print(filename)
    file = open(filename, "r")
    file_content = json.load(file)
    print(type(file_content))
    all_image_tags[filename[0:8]] = file_content
    file.close()

all_image_tags_file = open("../output/image_tags/all_image_tags.json", "w")
json.dump(all_image_tags, all_image_tags_file)
all_image_tags_file.close()
