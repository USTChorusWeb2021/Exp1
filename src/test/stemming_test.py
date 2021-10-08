from nltk.stem import PorterStemmer
import time

ps = PorterStemmer()

while True:
    word = input("stem>> ")
    start_time = time.time()
    stem = ps.stem(word)
    print(stem, time.time() - start_time)
