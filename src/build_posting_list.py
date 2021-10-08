# build_posting_list.py
# USTChorusWeb2021
# By HurryPeng & WhitieKitty

import json
import time

def main():
    time_start = time.time()

    corpus_file = open("../output/corpus.json", "r")
    corpus = json.load(corpus_file)
    corpus_file.close()

    print("Finished loading in {} seconds".format(time.time() - time_start))
    time_start = time.time()

    posting_list = {}
    for doc in corpus:
        path = doc["path"]
        for word in doc["text"]:
            try:
                current_list = posting_list[word]
                if current_list[-1] != path:
                    current_list.append(path)
            except KeyError:
                posting_list[word] = [path]
        print(path)

    posting_list_file = open("../output/posting_list.json", "w")
    json.dump(posting_list, posting_list_file)
    posting_list_file.close()

    print("Finished in {} seconds".format(time.time() - time_start))

if __name__ == "__main__":
    main()
