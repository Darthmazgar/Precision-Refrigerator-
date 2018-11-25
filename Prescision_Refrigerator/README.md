# Precision Refrigerator #

Python 3.6.1 code, which works with a Raspberry Pi interface to precisely Control
the temperature of a substance by alternating the state of a Peltier heat pump
operating on a separate current loop, which is toggled using a transistor switch.

The system is made up of two main classes; Thermometer and Cooler, with an optional add on of Fan
(template only).

### Run Programme ###

In main.py choose an aim temperature (tmp_aim); a precition level (precision); a mass of fluid (mass) in kg; 
the input voltage and current (v, i); then choose a convergence method and run main.py.

## Cooler ##

The cooler class controls the state of the cooling chip. Depending on the
temperature of a substance recorded by a thermometer, which is controlled by the Thermometer class.
Within the cooler class there are a series of different convergence methods which switch on and off
the cooling chip when certain criteria have been met. These methods are:
* **Converge**: Turns on the cooling chip when the temperature is above the aim temperature (+precision)
and off when below (-precision).
* **Hysteretic_conv**: Turns on the cooling chip when the temperature is above the aim temperature (+precision)
and off when below (-precision/2). This was chosen based on the assumption that the temperature will rise
quicker that it will fall, so limits the amount the temperature will fall by half as much as just Converge
alone.
* **Rate_limit_conv**: This takes measurements of the ambient room temperature and compares it to the aim temperature to find the rate at which the water temperature will be increasing. This is used to calculate how far above the aim temperature the precision should be set.
* **Pre_emp_conv**: This takes the average rate of temperature change over the last number of measurement steps (here 5  is used). If the average rate of temperature change is positive and the temperature is close to the aim temperature then the chip is switched off, pre-empting the point at which the temperature will go above the aim temperature, and the same process in reverse with a negative rate of change. Since it is assumed that the temperature will increase faster than it will decrease, due to the ambient temperature being relativly high, then the 'near' range about the aim temperature is less for the cooling direction (within 3 * the rate (per second)) than the heating direction (within 5 * the rate (per second)). 

All of the above cooling methods will cool to an aim temperature at which the temperature will oscillate in a
sinusoidal manner about the aim temperature with different amplitudes and frequencies depending on the
effectiveness of the convergence method.

On the first cooling phase the efficiency of the cooling system will be calculated.

![equation](http://latex.codecogs.com/gif.latex?Efficency%3D%5Cfrac%7BEnergyToCoolWater%7D%7BTotalEnergyUsed%7D)




## Thermometer ##

The thermometer class deals with the reading and recording of temperature. Every time a request for temperature data is made, that temperature is stored in an array of given length (arr_len). This array updates by removing the 0th element and adding the new data point in to the last position in the array. Following this the rate of temperature change can be found by comparing the two most recent temperatures and dividing by the time taken between readings to get a rate of temperature change in degrees per second. This updates an array in a similar manner to the temperature. Plots of these data can be made which live update when new data is colected.

The class also has functionality to calculate a percentage score of how closely the temperature data matched the aim temperature given (aim_tmp). This counts how many data are within a precision range of the aim temperature and divided by the total number of data to give a score.

Here plt.ion() was used to provide the live animation instead of FuncAnimation as this will allow for refreshable plots
to be made at the same time as performing other functions without musing multiple threads. 

## Cooling Data ##

The file cooling_data.py is used to generate reference heating and coling curves which show how the temperature varies with time when heating and cooling.

## Additional Files ##

### Analysis and Plotting ###

'plot_meth.py' Contains scripts which take temperature data and plot the data calculating statistical results such as the mean of the 
data, total error on the mean, reduced chi squared and percentage score.

'smooth_data.py' Shows examples of smoothed data when compared to raw data.

### Thermometer Calibration ### 

'therm_calib.py' Records the temperature data from two thermometers and plots the temperatures together to see the 
difference between the readings from the two thermometers in similar conditions.

'loaded_therm_calib.py' Exact same functionality as above but for loaded data in the form of a .txt file rather than recording the data live. 