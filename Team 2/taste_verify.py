'''
Splits the tastes.csv file into taste-specific files, taste_verify_<taste>.csv
These files are sorted in descending order of their respective taste scores
'''
import json

tastes = [
    "bitter",
    "rich",
    "salt",
    "sour",
    "sweet",
    "umami",
]


def clean(line):
    '''
    Cleans the input line string received
    and returns a tuple of the format
    (   dishid,
        bitter_score,
        rich_score,
        salt_score,
        sour_score,
        sweet_score,
        umami_score
    )
    '''
    linevalues = line.strip("\n").split(",")
    rlist = [linevalues[0]]
    for value in linevalues[1:]:
        rlist.append(round(float(value), 2))

    return tuple(rlist)


def stringify(item):
    '''
    Helper to format the string that is to be written
    into the taste-specific file
    Returns a string following the format
    dishid, dishname, taste_score
    '''
    return str(item[0]) + "," + str(item[1]) + "," + str(item[2]) + "\n"


idmapping = None

with open("dishid_mapping.json") as mapfile:
    idmapping = json.load(mapfile)

outfilehandles = [open("taste_verify_" + taste + ".csv", "w")
                  for
                  taste
                  in tastes]

tastevalues = [list() for taste in tastes]

with open("../Utilities/Team 2/tastes.csv") as tastefile:
    for line in tastefile:
        tlist = clean(line)
        for tasteindex in range(len(tastes)):
            tastevalues[tasteindex].append(
                (tlist[0], idmapping[tlist[0]], tlist[tasteindex + 1]))

for index in range(len(tastevalues)):
    tastevalues[index].sort(key=lambda item: item[2], reverse=True)

for tastefileindex in range(len(tastes)):
    for tastevalue in tastevalues[tastefileindex]:
        outfilehandles[tastefileindex].write(stringify(tastevalue))

for handle in outfilehandles:
    handle.close()
