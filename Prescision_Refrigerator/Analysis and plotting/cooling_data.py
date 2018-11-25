'''
Runs to record data while the cooling chip is on and stores the plot of this cooling data along with an 
output file of the data [Temp degrees celcius, time seconds] for each data point. 
This is set to record 1000 data points at about 1 per second ~17 mins cooling and then another ~17 heating.
'''

import numpy as np
import matplotlib.pyplot as plt
from Thermometer import Thermometer
from Cooler import Cooler
import RPi.GPIO as GPIO
from webiopi.devices.sensor.onewiretemp import DS18B20  # Import thermometer libraries.
from webiopi.devices.sensor.onewiretemp import DS18S20
import time


def write_to_file(x_data, y_data, out_file="Cooling_curve_data.txt"):
    f = open(out_file, 'w')
    for i in range(len(x_data)):
        f.write("[%f, %f] \n" % (x_data[i], y_data[i]))
    f.close()


def collect_data(length, therm):
    """
    Collects temperature data for a given length of data points.
    :param: Length: (int) The number of data points to be colected.
    :param: therm: (object) Thermometer object where the temperature can be fetched.
    :return: (float) tmp_arr, array of temperatures; (float) array of collection times.
    """
    tmp_arr = np.zeros(length)
    time_arr = np.zeros(length)
    st = time.time()
    for i in range(length):
        tmp_arr[i] = therm.get_tmp()
        time_arr[i] = time.time() - st
    return tmp_arr, time_arr


def plot_data(x_data, y_data, cooling=True):
    plt.plot(x_data, y_data)
    plt.xlabel("Time (s)")
    plt.ylabel("Temperature $^oC$")
    if cooling:
        plt.title("Cooling Reference Curve")
        plt.savefig("Cooling_data_curve.png")
    else:
        plt.title("Heating Reference Curve")
        plt.savefig("Heating_data_curve.png")
    plt.show()


def main():
    GPIO.setwarnings(False)  # Turn of warnings from GPIO.

    data_len = 1000

    tmp_aim = 15  # Low unreachable temperature in the time.
    room_tmp = Thermometer(DS18S20(slave="10-000802deb0fc"), GPIO=GPIO, name="room")
    water_tmp = Thermometer(DS18B20(slave="28-000006cb82c6"), GPIO=GPIO, name="water")
    cooler = Cooler(GPIO=GPIO, tmp_aim=tmp_aim, therm=water_tmp, tmp_amb=room_tmp, name="Peltier", input_pin=24)

    cooler.turn_on()
    cool_data, time_arr_c = collect_data(data_len, water_tmp)  # Collect cooling data.
    plot_data(time_arr_c, cool_data, True)
    write_to_file(cool_data, time_arr_c)  # Write cooling data to file.

    cooler.turn_off()
    heat_data, time_arr_h = collect_data(data_len, water_tmp)  # Collect heating data.
    plot_data(time_arr_h, heat_data, False)
    write_to_file(heat_data, time_arr_h, 'Heating_curve_data.txt')  # Write heating data to file.
    
main()
