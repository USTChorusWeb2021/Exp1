# semantic_search_backend.py
# USTChorusWeb2021
# By HurryPeng & WhitieKitty

import time
import json
from typing import Tuple
from nltk.stem import PorterStemmer
import queue

class SemanticSearcher:
    def __init__(self) -> None:
        self.tf_idf = None
        self.porter_stemmer = PorterStemmer()

    def loadTfIdf(self, path: str) -> None:
        tf_idf_file = open(path, "r")
        self.tf_idf = json.load(tf_idf_file)
        tf_idf_file.close()

    def semanticSearch(self, query: list, scope: list) -> Tuple[str, list]:
        if self.tf_idf == None:
            raise RuntimeError("Error: tf-idf matrix is not loaded")

        start_time = time.time()

        # keywords = query.split()
        best_matches_queue = queue.PriorityQueue()

        for article in scope:
            rating = 0.0
            compressed_article = article[6:9] + article[15:20]
            for keyword in query:
                keyword = self.porter_stemmer.stem(keyword)
                try:
                    # print(compressed_article, keyword)
                    # rating += self.tf_idf[compressed_article][keyword]
                    rating += eval(self.tf_idf[compressed_article][keyword])
                    # print(compressed_article, keyword, self.tf_idf[compressed_article][keyword])
                except Exception:
                    pass
            best_matches_queue.put((rating, article))
            if best_matches_queue.qsize() > 10:
                best_matches_queue.get()

        best_matches = []
        while not best_matches_queue.empty():
            best_matches.append(best_matches_queue.get())
        best_matches.reverse()

        return query.__str__(), best_matches
