import sys
import json
dictionary = dict()
smax = -sys.maxsize
smin = sys.maxsize

with open(sys.argv[1]) as filelines:
		for line in filelines:
				li = line.strip().split(":")
				dictionary[li[0].strip()] = float(li[1])
				if smax < float(li[1]):
						smax = float(li[1])
				if smin > float(li[1]):
						smin = float(li[1])
for key, value in dictionary.items():
	dictionary[key] = round((value - smin) / (smax - smin), 4)
with open(sys.argv[1].split(".")[0] + ".json", "w") as outfile:
	json.dump(dictionary, outfile, indent='\t')
