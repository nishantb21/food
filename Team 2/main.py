import argparse
import taster
import json
import os
import utilities


parser = argparse.ArgumentParser(prog="Taste Profiling of food items")
parser.add_argument("-p",
                    "--profile",
                    help="profile the specified dish", action='append')
parser.add_argument("-v",
                    "--validate",
                    nargs=3,
                    action="append",
                    metavar=("taste", "genscores", "surveyscores"),
                    help="Run the validator and "
                    "generate adjustment factors per taste.")
parser.add_argument("-c",
                    "--classify",
                    nargs=2,
                    action="append",
                    metavar=("/path/to/sample/file", "sample-size"),
                    help="Classify dishes listed in samples by taking sample-size items from the database"
                    )
arguments = parser.parse_args()

if arguments.profile:
    for dishfile in arguments.profile:
        for dish in utilities.read_json(dishfile):
            print("\n" + dish["dish_name"] + "\n" + "=" * len(dish["dish_name"]))
            print(json.dumps(taster.taste(dish), sort_keys=True, indent="  "))

if arguments.validate:
    from validator import Validator
    adjustment = dict()
    if os.path.exists("adjustment_factors.json"):
        adjustment = utilities.read_json("adjustment_factors.json")
    for vjob in arguments.validate:
        gendata = json.load(open(vjob[1]))
        survdata = json.load(open(vjob[2]))
        vobj = Validator(gendata, survdata)
        adjustment[vjob[0]] = vobj.adjustment_factor()
        print(json.dumps(adjustment, sort_keys=True, indent="  "))
    with open("adjustment_factors.json", "w") as adjfile:
        json.dump(adjustment, adjfile, indent="    ")

if arguments.classify:
    from cuisine_classifier import classify_cuisine
    db = utilities.read_json("../Utilities/Database/database.json")
    for cjob in arguments.classify:
        samplefile = utilities.read_json(cjob[0])
        for dish, value in classify_cuisine(db[:int(cjob[1])],
                                            samplefile).items():
            print("\n" + dish + "\n" + "=" * len(dish))
            for item in sorted(value, key=lambda x: x[1], reverse=True):
                print("{:14}: {:2}".format(item[0], round(item[1], 2)), end=' | ')
            print()
