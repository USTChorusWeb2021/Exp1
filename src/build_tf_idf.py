# building_tf_idf.py
# USTChorusWeb2021
# By HurryPeng & WhitieKitty

import json
import time
import math
from queue import PriorityQueue

def main():
    time_start = time.time()

    corpus_file = open("../output/corpus.json", "r")
    corpus = json.load(corpus_file)
    corpus_file.close()

    print("Finished loading in {} seconds.".format(time.time() - time_start))
    
    time_start = time.time()

    tf_idf_file = open("../output/tf_idf.json", "w")

    class Word:
        pass

    weak_posting_list = {}
    for doc in corpus:
        path = doc["path"]
        for word in doc["text"]:
            try:
                if weak_posting_list[word].last_currence != path:
                    weak_posting_list[word].last_currence = path
                    weak_posting_list[word].count += 1
            except KeyError:
                weak_posting_list[word] = Word()
                weak_posting_list[word].count = 1
                weak_posting_list[word].last_currence = path

    print("Finished building weak posting list.")

    word_stat_dict = {}
    for doc in corpus:
        path = doc["path"]
        word_stat_dict[path] = {}
        for word in doc["text"]:
            try:
                word_stat_dict[path][word] += 1
            except KeyError:
                word_stat_dict[path][word] = 1

    print("Finished building word_stat_dict")

    tf_idf = {}
    doc_total = len(word_stat_dict)
    q = PriorityQueue()
    for doc in word_stat_dict:
        tf_idf[doc] = {}
        for word in word_stat_dict[doc]:
            # print(word)
            # print(len(word_stat_dict[doc]))
            # print((weak_posting_list[word].count))
            tf = math.log10(word_stat_dict[doc][word]) + 1
            # print("tf", tf)
            idf = math.log10(doc_total / weak_posting_list[word].count)
            # print("idf", idf)
            q.put((tf * idf, word))
            if q.qsize() > 50:
                q.get()
        print("Finished priority queue for document {}".format(doc))
        while q.empty() == False:
            current_idf = q.get()
            # print(current_idf[0], current_idf[1])
            tf_idf[doc][current_idf[1]] = round(current_idf[0], 5)
        print(tf_idf[doc])
        print("Finished calculating tf-idf of {}".format(doc))

    json.dump(tf_idf, tf_idf_file)

    tf_idf_file.close()

    print("Finished dumping: {}".format(time.time() - time_start))

if __name__ == "__main__":
    main()
