# download_images.py
# USTChorusWeb2021
# By HurryPeng & WhitieKitty

import json
import os
import wget

def main():
    path = '../dataset/US_Financial_News_Articles/'
    subpath = ['2018_01/', '2018_02/', '2018_03/', '2018_04/', '2018_05/']

    for i in [0]:
        current_subpath = subpath[i]

        full_path = path + current_subpath
        file_list = os.listdir(full_path)

        #for file_name in file_list:
        for file_name in file_list[0:100]: # TODO: Change input scale
        #for file_name in [file_list[0]]:
            with open(full_path + file_name, encoding='utf-8') as f:
                word_tokens = []
                news_dict = json.load(f)
                image_url = news_dict["thread"]["main_image"]
                compressed_path = current_subpath[-2:] + file_name[0] + file_name[-10:-5]
                compressed_path = compressed_path.replace("/", "_")
                
                try:
                    print(image_url)
                    wget.download(image_url, "../output/images/" + compressed_path + ".jpg")
                    print("Downloaded {}".format(compressed_path))
                except Exception as e:
                    print(e)
                    print("Failed {}".format(compressed_path))
        
if __name__ == "__main__":
    main()
