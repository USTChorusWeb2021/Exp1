# image_tagger.py
# USTChorusWeb2021
# By HurryPeng & WhitieKitty

import json
import requests
import os

def main() -> None:
    api_info_file = open("./api_info.json", "r")
    api_info = json.load(api_info_file)
    api_info_file.close()
    api_key = api_info["api_key"]
    api_secret = api_info["api_secret"]

    image_folder = "../output/images/"
    image_list = os.listdir(image_folder)

    for image_name in image_list[0:1000]:
        try:
            response = requests.post(
                'https://api.imagga.com/v2/tags',
                auth=(api_key, api_secret),
                files={'image': open(image_folder + image_name, 'rb')})

            single_image_json_file = open("../output/image_tags/" + image_name[0:8] + ".json", "w")
            json.dump(response.json(), single_image_json_file)
            single_image_json_file.close()

            print("Tagged {}".format(image_name))
        except Exception:
            print("Failed {}".format(image_name))

if __name__ == "__main__":
    main()
