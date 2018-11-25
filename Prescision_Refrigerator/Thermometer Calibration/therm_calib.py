"""
Records temperature data from two thermometers and plots them together.
"""
import numpy as np
import matplotlib.pyplot as plt
from webiopi.devices.sensor.onewiretemp import DS18B20

t1 = DS18B20(slave="28-000005e94da7")
t2 = DS18B20(slave="28-000006cb82c6")

test_range = 200
tmp1 = np.zeros(test_range)
tmp2 = np.zeros(test_range)

for i in range(test_range):
    tmp1[i] = t1.getCelsius()
    tmp2[i] = t2.getCelsius()

mean = np.mean(tmp1)
mean2 = np.mean(tmp2)
dm = np.abs(mean - mean2)
std1 = np.std(tmp1)
std2 = np.std(tmp2)
print("mean1: %.3f, mean2: %.3f, dif: %.3f, std1: %.3f, std2: %.3f" % (mean, mean2, dm, std1, std2))

plt.plot(tmp1)
plt.plot(tmp2)
plt.title("Compatison between two thermometers in the same temperature conditions.", fontsize=8)
plt.suptitle("Thermometer Calibration")
plt.xlabel("Time Step (~1s)")
plt.ylabel("Temperature $^oC$")
plt.savefig("therm_calib.png")
plt.show()



np.savetxt("therm1_calib_data.txt", tmp1)
np.savetxt("therm2_calib_data.txt", tmp2)

