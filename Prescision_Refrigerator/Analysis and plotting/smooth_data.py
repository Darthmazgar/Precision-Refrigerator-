"""
PLot examples of smoothed vs raw data to visualise the differences between these two methods.
"""

import numpy as np
from scipy.interpolate import spline
import matplotlib.pyplot as plt


def smooth(data):
    x = [x for x in range(len(data))]
    new = np.linspace(x[0], x[-1], 100)
    sm = spline(x, data, new)  # Creates smoothed data.
    return new, sm


def plot(x_data, y_data, show=False, save=False):
    plt.plot(x_data, y_data)
    if show:
        plt.legend(["Raw", "Smoothed"])
        plt.title("Raw Data Compared to Smoothed Data")
        plt.xlabel("Time Step (~1s)")
        plt.ylabel("Temperature $^oC$")
        if save:
            plt.savefig("raw_vs_smoothed.png")
        plt.show()


def main():
    data = np.genfromtxt("conv_copy.txt")
    x = [x for x in range(len(data))]
    xn, smoothed = smooth(data)
    plot(x, data)
    plot(xn, smoothed, True)


main()
