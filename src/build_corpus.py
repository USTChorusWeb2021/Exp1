# build_corpus.py
# USTChorusWeb2021
# By HurryPeng & WhitieKitty

import json
from re import T
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from os import listdir
import time

def main():
    corpus = open('../output/corpus_fragment.json', 'w')
    corpus.write("")
    corpus.close()
    corpus = open('../output/corpus_fragment.json', 'a')
    time_start = time.time()

    stop_words = set(stopwords.words('english'))
    ps = PorterStemmer()
    punctuations = \
    [
        ',', '.', '!', '?', '(', ')', ';', '`', "'", '"', '$', '/',
        '\u200b', '\u200d', '‘', '’', ':', '-', '*', '“', '”', '|', 
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'
    ]

    def hasPunct(token: str) -> bool:
        for char in token:
            if char in punctuations:
                return True
        return False

    path = '../dataset/US_Financial_News_Articles/'
    subpath = ['2018_01/', '2018_02/', '2018_03/', '2018_04/', '2018_05/']

    for i in [0, 1, 2, 3, 4]:
        current_subpath = subpath[i]

        full_path = path + current_subpath
        file_list = listdir(full_path)

        #for file_name in file_list:
        for file_name in file_list[0:100]: # TODO: Change input scale
        #for file_name in [file_list[0]]:
            with open(full_path + file_name, encoding='utf-8') as f:
                word_tokens = []
                news_dict = json.load(f)
                sent_tokens = sent_tokenize(news_dict['text'] + (news_dict["title"] + ' ') * 8)
                # print(sent_tokens)    
                for sent_token in sent_tokens:
                    new_word_tokens = word_tokenize(sent_token)
                    word_tokens.extend(new_word_tokens)
                # print(word_tokens)
                text_filtered = []
                for w in word_tokens:
                    if  w not in stop_words and w.isalpha() and w != "":
                        text_filtered.append(ps.stem(w))

                compressed_path = current_subpath[-2:] + file_name[0] + file_name[-10:-5]

                news = \
                {
                    # 'title': news_dict['title'],
                    'path': compressed_path,
                    # 'url': news_dict['url'],
                    # 'image': news_dict['thread']['main_image'],
                    'text': text_filtered
                }
                
                # for person in news_dict['entities']['persons']:
                #     news['entities'].append(person['name'])
                # for location in news_dict['entities']['locations']:
                #     news['entities'].append(location['name'])
                # for organization in news_dict['entities']['organizations']:
                #     news['entities'].append(organization['name'])
                
                print(compressed_path)
                json.dump(news, corpus)
                corpus.write(',')

    corpus.close()
    print("Time", time.time() - time_start)
  
if __name__ == "__main__":
    main()
