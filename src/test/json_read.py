import json
import time

time_start = time.time()
test_file = open("../../output/corpus.json", "r")
d = json.load(test_file)
test_file.close()

input("Finished loading {}".format(time.time() - time_start))

while True:
    expr = input(">>> ")
    try:
        eval(expr)
    except Exception:
        pass
