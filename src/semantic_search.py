# semantic_search.py
# USTChorusWeb2021
# By HurryPeng & WhitieKitty

import os
import time
from nltk.stem import PorterStemmer
from nltk.corpus import wordnet
from nltk.util import pr

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
    print("    e.g. >> search china america trade war")
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
    try:
        raw_query = query.copy()

        option_synonym = False
        option_none_bool = False

        while len(query) != 0 and query[0].startswith("-"):
            if query[0] == "-s":
                option_synonym = True
                query = query[1:]
            elif query[0] == "-n":
                option_none_bool = True
                query = query[1:]
            else:
                raise SyntaxError()
        
        if len(query) == 0:
            raise SyntaxError()

        print("Received query: ")
        print(query)
        if option_synonym:
            print("Synonym search enabled")
        else:
            print("Synonym search disabled")
        if option_none_bool:
            print("Bool search preprocessing disabled")
        else:
            print("Bool search preprocessing enabled")

        start_time = time.time()

        if option_synonym:
            query_with_syn = []
            for word in query:
                for syn in wordnet.synsets(word):
                    for lm in syn.lemmas():
                        query_with_syn.append(lm.name())
            query = query_with_syn
            query = list(set(query)) # remove repeated items
            print("Query with synonyms")
            print(query)

        query = [porter_stemmer.stem(word) for word in query]
        query.sort()
        
        bool_search_query = ""
        for i in range(0, len(query)):
            bool_search_query += query[i]
            if i != len(query) - 1:
                bool_search_query += " OR "
        
        scope = []
        if option_none_bool:
            all_articles = bool_searcher.all_articles_list
            for article in all_articles:
                article_str: str = "2018_0%1d/" % (article >> 17)
                if (article >> 16) & 0b1 != 0:
                    article_str += "news_00%05d"
                else:
                    article_str += "blogs_00%05d"
                article_str %= (article & 0xffff)
                scope.append(article_str)
        else:
            bool_format_query, scope = bool_searcher.boolSearch(bool_search_query)

        sem_format_query, best_matches = semantic_searcher.semanticSearch(query, scope)
        elapse = time.time() - start_time
        # print(scope)
        # print(query)
        # print(bool_search_query)
        results = [term[1] for term in best_matches]

        print("Finished searching in {} seconds".format(elapse))

        print("Best matches: ")
        print(print(best_matches))

        result_file = open("../output/result.html", "w", encoding='utf-8')
        result_file.write(result_gen.generate("Semantic", raw_query, elapse, results))
        result_file.close()

        os.startfile(os.getcwd() + "/../output/result.html")

        print("Result page generated")
    
    except RuntimeError:
        print("RuntimeError: tf-idf matrix is not loaded")
    except SyntaxError:
        print("Wrong argument format")

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
