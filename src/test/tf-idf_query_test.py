import json
import time
import queue

time_start = time.time()

dataset = dict()
for i in range(0, 300000):
    dataset["{}".format(i)] = [j for j in range(1000000 * i, 1000000 * i + 300)]

print("Finished Building Dict {}".format(time.time() - time_start))
time_start = time.time()

vec = [j for j in range(0, 300)]

result = queue.PriorityQueue()

for i in range(0, 300000):
    score = 0
    for j in range(0, 300):
        score += vec[j] * dataset["{}".format(i)][j]

    result.put((score, "{}".format(i)))
    if result.qsize() > 10:
        result.get()

while result.qsize() != 0:
    print(result.get())

input("Finished Query {}".format(time.time() - time_start))

