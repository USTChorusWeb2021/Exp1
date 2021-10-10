# build_posting_list.py
# USTChorusWeb2021
# By HurryPeng & WhitieKitty

import json
import time
import struct

def main():
    time_start = time.time()

    corpus_file = open("../output/corpus.json", "r")
    corpus = json.load(corpus_file)
    corpus_file.close()

    print("Finished loading in {} seconds".format(time.time() - time_start))
    time_start = time.time()

    posting_list_file = open("../output/posting_list.bin", "wb")

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

        heading = ((eval(path[0])) << 1) + (path[1] == 'n')
        heading_bytes = heading.to_bytes(1, 'big')
        posting_list_file.write(heading_bytes)
        number = int(path[3:8])
        number_bytes = number.to_bytes(2, 'big')
        posting_list_file.write(number_bytes)
        print(path)

    # End of file name list & End of each word
    end_flag = 0
    EOFL_bytes = end_flag.to_bytes(3, 'big')
    EOW_bytes = end_flag.to_bytes(1, 'big')
    posting_list_file.write(EOFL_bytes)

    for key_word in posting_list:
        print("dumping:{}".format(key_word))
        current_word = posting_list[key_word]
        for i in range(0, len(key_word)):
            letter_ascii = ord(key_word[i])
            letter_byte = letter_ascii.to_bytes(1, 'big')
            posting_list_file.write(letter_byte)

        # End of a word
        posting_list_file.write(EOW_bytes)

        # Dump the articles which contain this word
        for j in range(0, len(current_word)):
            if j == len(current_word) - 1 : # end of current list
                article_heading = 0x80 # header begin with 1
            else:
                article_heading = 0x00
            article_heading += ((eval(current_word[j][0])) << 1) + (current_word[j][1] == 'n')
            article_heading_bytes = article_heading.to_bytes(1, 'big')
            posting_list_file.write(article_heading_bytes)

            article_number = int(current_word[j][3:8])
            article_number_bytes = article_number.to_bytes(2, 'big')
            posting_list_file.write(article_number_bytes)
        



    posting_list_file.close()

    print("Finished in {} seconds".format(time.time() - time_start))

if __name__ == "__main__":
    main()
