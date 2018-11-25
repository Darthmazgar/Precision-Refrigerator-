"""
Loads temperature data from .txt files and plots together.
"""

import matplotlib.pyplot as plt
import numpy as np

tmp1 = np.genfromtxt("therm1_calib_data_low.txt")
tmp2 = np.genfromtxt("therm2_calib_data_low.txt")

tmp1 = tmp1[1:]  # Remove erroneous data in the 1st point
tmp2 = tmp2[1:]

mean = np.mean(tmp1)
mean2 = np.mean(tmp2)
dm = np.abs(mean - mean2)
std1 = np.std(tmp1)
std2 = np.std(tmp2)
print("mean1: %.3f, mean2: %.3f, dif: %.3f, std1: %.3f, std2: %.3f" % (mean, mean2, dm, std1, std2))

plt.plot(tmp1)
plt.plot(tmp2)
plt.title("Comparison between two thermometers in the same temperature conditions.", fontsize=8)
plt.suptitle("Thermometer Calibration")
plt.xlabel("Time Step (~1s)")
plt.ylabel("Temperature $^oC$")
# plt.savefig("therm_calib_low.png")
plt.show()



