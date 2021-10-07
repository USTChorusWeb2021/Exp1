import json
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from os import listdir
import time

def main():
    path = '../dataset/US_Financial_News_Articles/'
    subpath = ['2018_01/', '2018_02/', '2018_03/', '2018_04/', '2018_05/']

    # class News:
    #     """存储每篇新闻的标题, URL, 文本等用于检索的基本信息"""

    #     def __init__(self, title, url, image, text):
    #         self.title = title
    #         self.url = url
    #         self.image = image
    #         self.text = text
    #         self.entities = []

    stop_words = set(stopwords.words('english'))
    ps = PorterStemmer()
    punctuations = [',','.','!','?','(',')',';','``',"''",'$']

    full_path = path + subpath[0]
    file_list = listdir(full_path)

    corpus = open('../output/corpus_fragment.json', 'w')
    corpus.write("")
    corpus.close()
    
    corpus = open('../output/corpus_fragment.json', 'a')

    time_start = time.time()

    #for file_name in file_list:
    for file_name in file_list[0:1000]:
    #for file_name in [file_list[0]]:
        with open(full_path + file_name, encoding='utf-8') as f:
            word_tokens = []
            news_dict = json.load(f)
            sent_tokens = sent_tokenize(news_dict['text'])   
            # print(sent_tokens)    
            for sent_token in sent_tokens:
                new_word_tokens = word_tokenize(sent_token)
                word_tokens.extend(new_word_tokens)
            # print(word_tokens)
            text_filtered = []
            for w in word_tokens:
                if w not in stop_words and w not in punctuations:
                    text_filtered.append(ps.stem(w))

            news = {'title': news_dict['title'], 'url': news_dict['url'], 
            'image':news_dict['thread']['main_image'], 
            'text':text_filtered, 'entities':[]}
            for person in news_dict['entities']['persons']:
                news['entities'].append(person['name'])
            for location in news_dict['entities']['locations']:
                news['entities'].append(location['name'])
            for organization in news_dict['entities']['organizations']:
                news['entities'].append(organization['name'])
            
            print(file_name)
            json.dump(news, corpus)
            corpus.write(',')
    corpus.close()

    print("Time", time.time() - time_start)
  
if __name__ == "__main__":
    main()
