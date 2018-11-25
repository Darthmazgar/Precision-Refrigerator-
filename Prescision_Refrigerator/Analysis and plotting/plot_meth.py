"""
Very rough code used to plot the various convergence methods and calculate
statistics such as the mean, chi squared, total error and percentage score
of each method.
"""

import matplotlib.pyplot as plt
import numpy as np

conv = np.genfromtxt("conv_copy.txt")
conv = conv[:500]
hyst = np.genfromtxt("hyst_copy.txt")
hyst = hyst[:500]
pre = np.genfromtxt("pre_copy.txt")
pre = pre[:500]
rate = np.genfromtxt("rate_copy.txt")
rate = rate[:500]
meth = [conv, hyst, pre, rate]
x_data = [x for x in range(len(conv))]

avg = []
mm = []
chi_arr = []
sig_arr = []
tot_err = []
score = []

for meth in meth:
    avg.append(np.average(meth))
    mm.append([np.max(meth), np.min(meth)])
    chi = 0
    sig = 0
    count = 0
    for i in range(len(meth)):
        chi += (meth[i] - 21.4)**2 / 0.0625
        sig += (meth[i] - avg[-1])**2 / len(meth)
        if (meth[i] - 21.4) <= 0.0625:
            count += 1

    chi /= len(meth)
    chi_arr.append(chi)
    sig = np.sqrt(sig)
    sig_arr.append(sig)
    tot_err.append(np.sqrt(sig_arr[-1]**2 + 0.0625**2))
    score.append((count / len(meth)) * 100)

print("Average temp:     Conv : %.2f(6)^oC  Hyst : %.2f(6)^oC  Pre : %.2f(6)^oC    Rate : %.2f(6)^oC" % (avg[0], avg[1], avg[2], avg[3]))
print("Chi squared:      Conv : %.5f      Hyst : %.5f      Pre : %.5f        Rate : %.5f" % (chi_arr[0], chi_arr[1], chi_arr[2], chi_arr[3]))
print("Total error:      Conv : %.5f      Hyst : %.5f      Pre : %.5f        Rate : %.5f" % (tot_err[0], tot_err[1], tot_err[2], tot_err[3]))
print("Score:            Conv : %.1f%%        Hyst : %.1f%%        Pre : %.1f%%          Rate : %.1f%%" % (score[0], score[1], score[2], score[3]))

plt.plot(x_data, conv, label="Converge")
plt.plot(x_data, hyst, label="Hysteresis Converge")
plt.plot(x_data, pre, label="Pre-emptive Converge")
plt.plot(x_data, rate, label="Rate Limit Converge")
plt.legend()
plt.title("Convergence Methods Compared")
plt.xlabel("Time Step (~1s)")
plt.ylabel("Temperature $(^oC)$")
# plt.savefig("rate_lim.jpg")
plt.show()
