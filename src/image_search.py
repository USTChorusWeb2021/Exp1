# image_search.py
# USTChorusWeb2021
# By HurryPeng & WhitieKitty

import os
import json
import time
import queue
from nltk.stem import PorterStemmer

from generate_result import ImageResultGen

image_result_gen = ImageResultGen()

image_tags = None
porter_stemmer = PorterStemmer()

def printWelcomeMsg() -> None:
    print("Welcome to USTChorusWeb2021 image search console.")
    print("Enter \"help\" for help.")

def printHelpMsg() -> None:
    print("help: print help message")
    print("load [(optional) path]: load image tags")
    print("search [boolean expression]: do bool search with boolean expression")
    print("    e.g. >> search war AND (iraq OR iran) AND (NOT (britain OR england) AND NOT (us OR usa OR america)) AND australia")
    print("exit: bye!")

def loadImageTags(path: str) -> None:
    if path == "":
        path = "../output/image_tags/all_image_tags.json"
    print("Loading image tags from \"{}\"".format(path))
    print("This may take about 3 seconds")

    all_image_tags_file = open(path, "r")
    image_tags_temp = json.load(all_image_tags_file)
    all_image_tags_file.close()

    global image_tags
    image_tags = dict()

    for article in image_tags_temp:
        if image_tags_temp[article]["status"]["type"] != "success":
            continue
        article_regulated = article.replace("_", "/")
        image_tags[article_regulated] = []
        for confidence_tag_pair in image_tags_temp[article]["result"]["tags"]:
            image_tags[article_regulated].append(
                (
                    # porter_stemmer.stem(confidence_tag_pair["tag"]["en"]),
                    confidence_tag_pair["tag"]["en"],
                    confidence_tag_pair["confidence"]
                )
            )
        image_tags[article_regulated].sort()
    
    print("Load complete")

def imageSearch(query: str) -> None:
    print("Received query string: ")
    print(query)

    start_time = time.time()
    
    try:
        if image_tags == None:
            raise RuntimeError()
        
        query_list = query.split()
        # query_list = [porter_stemmer.stem(word) for word in query_list]
        query_list.sort()
        best_matches_queue = queue.PriorityQueue()

        for article in image_tags:
            arith_rating = 0.0
            geo_rating = 1.0
            i = 0
            j = 0
            while i < len(image_tags[article]) and j < len(query_list):
                word_confidence_pair = image_tags[article][i]
                current_keyword = query_list[j]
                if word_confidence_pair[0] < current_keyword:
                    i = i + 1
                elif word_confidence_pair[0] > current_keyword:
                    j = j + 1
                else:
                    arith_rating += word_confidence_pair[1]
                    geo_rating *= word_confidence_pair[1]
                    i = i + 1
                    j = j + 1
            arith_rating /= len(query_list)
            geo_rating = geo_rating ** (1 / len(query_list))
            if j != len(query_list):
                geo_rating = 0.0
            rating = geo_rating * 0.9 + arith_rating * 0.1
            best_matches_queue.put((rating, article))
            if best_matches_queue.qsize() > 12:
                best_matches_queue.get()

        best_matches = []
        while not best_matches_queue.empty():
            best_matches.append(best_matches_queue.get())
        best_matches.reverse()
        # for i in range(0, len(best_matches)):
        #     pair = best_matches[i]
        #     new_pair = (pair[0], pair[1].replace("1/b", "01/blogs_00"))
        #     best_matches[i] = new_pair

        # print(best_matches)

        elapse = time.time() - start_time
        print("Finished searching in {} seconds".format(elapse))

        result_file = open("../output/result.html", "w", encoding='utf-8')
        result_file.write(image_result_gen.generate(query_list, elapse, best_matches))
        result_file.close()

        os.startfile(os.getcwd() + "/../output/result.html")

        print("Result page generated")
    
    except RuntimeError:
        print("RuntimeError: image tags are not loaded")
    except SyntaxError:
        print("SyntaxError: wrong query format")

def evalMode() -> None:
    while True:
        try:
            eval_command = input(">>> ")
            if eval_command == "exit()":
                break
            eval(eval_command)
        except Exception as e:
            print(e)

def main() -> int:
    printWelcomeMsg()

    while (True):
        raw_command = input(">> ")
        commands = raw_command.split()

        if (len(commands) == 1 and (commands[0] == "exit" or commands[0] == "bye")):
            print("bye!")
            return 0
        elif (len(commands) == 1 and commands[0] == "help"):
            printHelpMsg()
        elif (commands[0] == "load"):
            loadImageTags(raw_command[len(commands[0]) + 1:])
        elif (len(commands) > 1 and commands[0] == "search"):
            imageSearch(raw_command[len(commands[0]) + 1:])
        elif (commands[0] == "eval"):
            evalMode()
        else:
            print("Unknown command. Enter \"help\" for help.")
        
if __name__ == "__main__":
    main()
