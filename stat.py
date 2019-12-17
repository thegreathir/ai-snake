import sys
import statistics

f = open(sys.argv[1], "r")

data = [int(x.split(" ")[0]) for x in f.read().split("\n") if x != '']

print ("max", max(data))
print ("min", min(data))
print ("avg", statistics.mean(data))
print ("variance", statistics.variance(data))
