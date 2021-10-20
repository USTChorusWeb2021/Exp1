# semantic_search.py
# USTChorusWeb2021
# By HurryPeng & WhitieKitty

# image_search.py
# USTChorusWeb2021
# By HurryPeng & WhitieKitty

import os
import json
import time
import queue
from nltk.stem import PorterStemmer
from bool_search import boolSearch

from bool_search_backend import BoolSearcher
from semantic_search_backend import SemanticSearcher
from generate_result import ResultGen

porter_stemmer = PorterStemmer()
bool_searcher = BoolSearcher()
semantic_searcher = SemanticSearcher()
result_gen = ResultGen()

def printWelcomeMsg() -> None:
    print("Welcome to USTChorusWeb2021 semantic search console.")
    print("Enter \"help\" for help.")

def printHelpMsg() -> None:
    print("help: print help message")
    print("load [(optional) path0] [(optional) path1]: load posting list from path0 and tf-idf matrix from path1")
    print("search [query]: do semantic search with query")
    print("    e.g. >> search iraq war oil")
    print("exit: bye!")

def loadTfIdf(path0: str, path1: str) -> None:
    if path0 == "":
        path0 = "../output/posting_list.bin"
    if path1 == "":
        path1 = "../output/tf_idf.json"
    
    print("Loading posting list from \"{}\"".format(path0))
    print("This may take about 20 seconds")
    bool_searcher.loadPostingList(path0)

    print("Loading tf-idf matrix from \"{}\"".format(path1))
    print("This may take about 5 seconds")
    semantic_searcher.loadTfIdf(path1)

    print("Load complete")

def semanticSearch(query: list) -> None:
    print("Received query: ")
    print(query)

    start_time = time.time()
    
    try:
        query = [porter_stemmer.stem(word) for word in query]
        query.sort()
        
        bool_search_query = ""
        for i in range(0, len(query)):
            bool_search_query += query[i]
            if i != len(query) - 1:
                bool_search_query += " OR "
        
        bool_format_query, scope = bool_searcher.boolSearch(bool_search_query)
        sem_format_query, best_matches = semantic_searcher.semanticSearch(query, scope)
        elapse = time.time() - start_time
        # print(scope)
        # print(query)
        # print(bool_search_query)
        print(best_matches)
        results = [term[1] for term in best_matches]

        print("Finished searching in {} seconds".format(elapse))

        result_file = open("../output/result.html", "w", encoding='utf-8')
        result_file.write(result_gen.generate("Semantic", sem_format_query, elapse, results))
        result_file.close()

        os.startfile(os.getcwd() + "/../output/result.html")

        print("Result page generated")
    
    except RuntimeError:
        print("RuntimeError: tf-idf matrix is not loaded")

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
        elif (commands[0] == "load" and len(commands) == 1):
            loadTfIdf("", "")
        elif (commands[0] == "load" and len(commands) == 3):
            loadTfIdf(commands[1], commands[2])
        elif (len(commands) > 1 and commands[0] == "search"):
            semanticSearch(commands[1:])
        elif (commands[0] == "eval"):
            evalMode()
        else:
            print("Unknown command. Enter \"help\" for help.")
        
if __name__ == "__main__":
    main()
