#!/usr/bin/env python

import matplotlib as mpl


#dark
# BB BB CC CC C C B B
# 03 02 01 __ 0 1 _ _

#light
# BB BB CC CC C C B B
# __ __ 01 00 _ 1 2 3

# -> edges/labels (black): 0/00
# -> inner face   (white): 03/3
# -> outer face   (grey):  02/2


base03  = "#002b36"
base02  = "#073642"
base01  = "#586e75"
base00  = "#657b83"
base0   = "#839496"
base1   = "#93a1a1"
base2   = "#eee8d5"
base3   = "#fdf6e3"
yellow  = "#b58900"
orange  = "#cb4b16"
red     = "#dc322f"
magenta = "#d33682"
violet  = "#6c71c4"
blue    = "#268bd2"
cyan    = "#2aa198"
green   = "#859900"


color_cycles = {
    "def":  "bgrcmvk",
    "def+": "bgrcmvkoy",
    "mpl":  "bgrcmyk",
    "mpl+": "bgrcmykov",
    "sol":  "kyormvbcg",
}



def make_cycler(color_dict, color_string):
    lst = [color_dict[c] for c in color_string]
    cyc = mpl.cycler(color=lst)
    return cyc


def setup(color="def", lines_only=True, dark=False):

    if color in color_cycles:
        color = color_cycles[color]

    if dark:
        black = base0
        grey  = base02
        white = base03
    else:
        black = base00
        grey  = base2
        white = base3

    color_dict = {
        "y": yellow,
        "o": orange,
        "r": red,
        "m": magenta,
        "v": violet,
        "b": blue,
        "c": cyan,
        "g": green,
        "k": black,
        "e": grey,
        "w": white
    }

    color_cycler = make_cycler(color_dict, color)

    params = {
        "axes.prop_cycle": color_cycler
    }

    if not lines_only:
        params.update({
            "axes.edgecolor":    black, # k
            "axes.facecolor":    white, # w
            "axes.labelcolor":   black, # k
            "figure.edgecolor":  white, # w
            "figure.facecolor":  grey,  # 0.75
            "grid.color":        black, # k
            "patch.edgecolor":   black, # k
            "patch.facecolor":   blue,  # b
            "savefig.facecolor": grey,  # w
            "text.color":        black, # k
            "xtick.color":       black, # k
            "ytick.color":       black, # k
        })

    mpl.rcParams.update(params)



setup()





if __name__ == "__main__":
    setup(color="def+", lines_only=False, dark=True)

    import numpy as np
    np.random.seed(0)

    from matplotlib import pyplot as plt
    import matplotlib
    matplotlib.rc("lines", linewidth=2, markeredgewidth=2, markersize=8)

    ncurves = 9
    npoints = 20

    for i in range(ncurves):
        offset = ncurves - i - 1
        name = str(i + 1)
        A = np.random.random(npoints) + offset
        plt.plot(A, "x-", label=name)

    plt.legend(loc="best")
    plt.show()



