# bool_search.py
# USTChorusWeb2021
# By HurryPeng & WhitieKitty

import os
import time

from bool_search_backend import BoolSearcher
from generate_result import ResultGen

bool_searcher = BoolSearcher()
result_gen = ResultGen()

def printWelcomeMsg() -> None:
    print("Welcome to USTChorusWeb2021 bool search console.")
    print("Enter \"help\" for help.")

def printHelpMsg() -> None:
    print("help: print help message")
    print("load [(optional) path]: load posting list, from default path if second parameter is ignored")
    print("search [boolean expression]: do bool search with boolean expression")
    print("    e.g. >> search war AND (iraq OR iran) AND (NOT (britain OR england) AND NOT (us OR usa OR america)) AND australia")
    print("exit: bye!")

def loadPostingList(path: str) -> None:
    if path == "":
        path = "../output/posting_list.bin"
    print("Loading posting list from \"{}\"".format(path))
    print("This may take about 20 seconds")

    bool_searcher.loadPostingList(path)
    
    print("Load complete")

def boolSearch(query: str) -> None:
    print("Received query string:")
    print(query)

    start_time = time.time()
    
    try:
        formatted_query, articles = bool_searcher.boolSearch(query)

        print("Resolved boolean expression: ")
        print(formatted_query)

        elapse = time.time() - start_time

        print("Finished searching in {} seconds".format(elapse))
        print("Found {} matching result(s)".format(len(articles)))

        result_file = open("../output/result.html", "w", encoding='utf-8')
        result_file.write(result_gen.generate("Bool", formatted_query, elapse, articles))
        result_file.close()

        os.startfile(os.getcwd() + "/../output/result.html")

        print("Result page generated")
    
    except RuntimeError:
        print("RuntimeError: posting list is not loaded")
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
            loadPostingList(raw_command[len(commands[0]) + 1:])
        elif (len(commands) > 1 and commands[0] == "search"):
            boolSearch(raw_command[len(commands[0]) + 1:])
        elif (commands[0] == "eval"):
            evalMode()
        else:
            print("Unknown command. Enter \"help\" for help.")
        
if __name__ == "__main__":
    main()
