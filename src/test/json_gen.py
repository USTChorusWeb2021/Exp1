import json
import time

time_start = time.time()

dataset = dict()
for i in range(0, 10000):
    dataset["{}".format(i)] = [j for j in range(10000 * i, 10000 * i + 10000)]

input("Finished building dict {}".format(time.time() - time_start))

time_start = time.time()
test_file = open("test_file.json", "w")
json.dump(dataset, test_file)
test_file.close()

input("Finished dumping {}".format(time.time() - time_start))

