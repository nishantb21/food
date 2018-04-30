import argparse
import taster
import json
import os


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
arguments = parser.parse_args()

if arguments.profile:
    for dishfile in arguments.profile:
        with open(dishfile) as dfile:
            taster.taste(json.load(dfile))

if arguments.validate:
    from validator import Validator
    adjustment = dict()
    if os.path.exists("adjustment_factors.json"):
        with open("adjustment_factors.json") as adjfile:
            adjustment = json.load(adjfile)
    for vjob in arguments.validate:
        gendata = json.load(open(vjob[1]))
        survdata = json.load(open(vjob[2]))
        adjustment[vjob[0]] = Validator(gendata, survdata).adjustment_factor()
    with open("adjustment_factors.json", "w") as adjfile:
        json.dump(adjustment, adjfile, indent="    ")
