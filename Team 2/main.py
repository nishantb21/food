import argparse
import taster
import json
import os
import utilities
from math import pi
import matplotlib.pyplot as plt


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
                    help="Classify dishes listed in samples by taking"
                    " sample-size items from the database"
                    )
arguments = parser.parse_args()


def show_graph(data):

    # Set data
    cat = list(data.keys())
    values = list(data.values())

    N = len(cat)

    x_as = [n / float(N) * 2 * pi for n in range(N)]

    # Because our chart will be circular we need to append a copy of the first
    # value of each list at the end of each list with data
    values += values[:1]
    x_as += x_as[:1]

    # Set color of axes
    plt.rc('axes', linewidth=0.5, edgecolor="#888888")

    # Create polar plot
    ax = plt.subplot(111, polar=True)

    # Set clockwise rotation. That is:
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)

    # Set position of y-labels
    ax.set_rlabel_position(0)

    # Set color and linestyle of grid
    ax.xaxis.grid(True, color="#888888", linestyle='solid', linewidth=0.5)
    ax.yaxis.grid(True, color="#888888", linestyle='solid', linewidth=0.5)

    # Set number of radial axes and remove labels
    plt.xticks(x_as[:-1], [])

    # Set yticks
    plt.yticks([2, 4, 6, 8, 10], ["2", "4", "6", "8", "10"])

    # Plot data
    ax.plot(x_as, values, linewidth=0, linestyle='solid', zorder=3)

    # Fill area
    ax.fill(x_as, values, 'b', alpha=0.3)

    # Set axes limits
    plt.ylim(0, 10)

    # Draw ytick labels to make sure they fit properly
    for i in range(N):
        angle_rad = i / float(N) * 2 * pi

        if angle_rad == 0:
            ha, distance_ax = "center", 1
        elif 0 < angle_rad < pi:
            ha, distance_ax = "left", 1
        elif angle_rad == pi:
            ha, distance_ax = "center", 1
        else:
            ha, distance_ax = "right", 1

        ax.text(angle_rad,
                10 + distance_ax,
                cat[i],
                size=10,
                horizontalalignment=ha,
                verticalalignment="center")

    # Show polar plot
    plt.show()


if arguments.profile:
    for dishfile in arguments.profile:
        for dish in utilities.read_json(dishfile):
            print("\n" + dish["dish_name"] + "\n" + "=" * len(dish["dish_name"]))
            data = taster.taste(dish)
            print(json.dumps(data, sort_keys=True, indent="  "))
            show_graph(data)

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
