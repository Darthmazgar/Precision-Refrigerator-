import time
import numpy as np
import sys


class Cooler(object):
    def __init__(self, GPIO, tmp_aim, therm, tmp_amb, name, precision=.1, input_pin=24):
        """
        Cooler class which controls the state of the cooling element through various convergence methods.
        :param GPIO: (class) GPIO class from RPi.GPIO library.
        :param tmp_aim: (float) The aim temperature in degrees Celsius.
        :param therm: (object) Thermometer class object measuring the temperature of the substance.
        :param tmp_amb: (object) Thermometer class object measuring the ambient (room) temperature.
        :param name: (string) Cooler name.
        :param precision: (float) Range around aim temperature that the cooler will operate.
        :param input_pin: (float) Pin number where the cooler state is controlled.
        """
        self.ip = input_pin
        self.GPIO = GPIO
        self.tmp_aim = tmp_aim
        self.therm = therm
        self.amb_therm = tmp_amb
        self.name = name
        self.precision = precision

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.ip, GPIO.OUT)  # Set pin as an output

        self.on_time = 0  # Initialize on times.
        self.init_time = 0
        self.final_time = 0

        self.total_on_time = 0
        self.on = False  # Set initial on/off state

        self.first_on = False
        self.first_off = False
        self.eff_calced = False

    def get_tmp_aim(self):
        """
        :return: (float) Current aim temperature.
        """
        return self.tmp_aim

    def set_tmp_aim(self, tmp, pr=False):
        """
        Sets the aim temperature of the cooling unit.
        :param tmp: (float) New aim temperature in degrees C.
        :param pr: (boolean) Print new aim temperature.
        :return: (float) Current aim temperature.
        """
        self.tmp_aim = tmp
        self.therm.tmp_aim = tmp  # Reset tmp aim for the Thermometer class
        if pr:
            print("Temperature aim set to %.2f degrees." % self.tmp_aim)
        return self.tmp_aim

    def get_precision(self):
        """
        :return: Current precision level of the cooling unit.
        """
        return self.precision

    def set_precision(self, pre, pr=False):
        """
        Sets the precision of the Cooler class with the min_precision of the given thermometer as a default minimum.
        :param pre: (float) Precision tmp +/- precision.
        :param pr: Print confirming change.
        :return: New changed precision.
        """
        self.precision = pre
        if pre < self.therm.min_precision:
            self.precision = self.therm.min_precision
            print("Set below minimum precision of thermometer.")
        if pr:
            print("Precision of %s set to %.2f degrees." % (self.name, self.precision))
        return self.precision

    def get_total_on_time(self):
        """
        Calculates the total time the cooling chip has been on.
        :return: (float) Total on time in seconds.
        """
        if self.on:
            return self.total_on_time + (time.time() - self.on_time)
        else:
            return self.total_on_time

    def turn_on(self):
        """
        Turns on the cooling chip and records the time the chip is turned on.
        :return: True when complete.
        """
        self.GPIO.output(self.ip, self.GPIO.HIGH)  # Turn on the cooling chip.
        if not self.on:
            print("Cooling chip: ON")
        self.on = True
        self.on_time = time.time()

        # Set up for measuring the energy used.
        if not self.first_on:
            self.first_on = self.therm.get_tmp()
            self.init_time = time.time()
        return True

    def turn_off(self):
        """
        Turns off the cooling chip and records the total on time of the chip by taking the difference between the
        current off time and the start time.
        :return: False when complete.
        """
        self.GPIO.output(self.ip, self.GPIO.LOW)  # Turn off the cooling chip.
        if self.on:
            print("Cooling chip: OFF")
        self.on = False
        self.total_on_time += time.time() - self.on_time  # Set the total on time.

        # Set up for measuring the energy used.
        if not self.first_off and self.first_on:
            self.first_off = self.therm.get_tmp()
            self.final_time = time.time()

        return False

    def converge(self):
        """
        Method to set the state of the cooling chip to converge on the aim_tmp.
        Turns on if the temperature of the substance is above the aim_tmp and turns off when below.
        :return: The difference in temperate between the current temperature and the aim_tmp.
        """
        tmp = self.therm.get_tmp()
        tmp_dif = np.abs(self.tmp_aim - tmp)

        if tmp != self.tmp_aim:
            if tmp < self.tmp_aim and tmp_dif > self.precision:
                self.turn_off()

            if tmp > self.tmp_aim and tmp_dif > self.precision:
                self.turn_on()

        return tmp_dif

    def hysteretic_conv(self):
        """
        Crude hysteretic convergence method where the high limit before the cooling chip is turned on is half that of
        the limit before the chip is turned off.
        :return: The difference in temperate between the current temperature and the aim_tmp.
        """
        tmp = self.therm.get_tmp()
        tmp_dif = np.abs(self.tmp_aim - tmp)

        if tmp != self.tmp_aim:
            if tmp < self.tmp_aim and tmp_dif > self.precision:
                self.turn_off()

            if tmp > self.tmp_aim and tmp_dif > self.precision / 2:  # since room tmp is higher then reduce the heating time as it will take longet to cool than it will to heat.
                self.turn_on()

        return tmp_dif

    def rate_limit_conv(self):
        """
        Reduces the upper limit that the temperature can reach before switching on the cooling chip based on
        the expected heating rate obtained from the difference between the temperature and the heating room temperature.
        """
        tmp = self.therm.get_tmp()
        tmp_dif = np.abs(self.tmp_aim - tmp)
        upper = self.upper_limit()

        if tmp != self.tmp_aim:
            if tmp < self.tmp_aim and tmp_dif > self.precision:
                self.turn_off()

            if tmp > self.tmp_aim and tmp_dif > upper:
                self.turn_on()

    def upper_limit(self):
        """
        Calculates upper limit based on ambient and aim temperatures
        :return: (float) Upper temperature limit in degrees.
        """
        amb = self.amb_therm.get_tmp()
        upper = self.precision / (amb - self.tmp_aim)
        return upper

    def pre_empt_conv(self, rate):
        """
        Truns on and of the cooling chip before the temperature has changed to being above or below the aim temperature
        respectively based on the rate of change over the last few time steps.
        :param rate: (float) Average temperature rate of change over the last 5 time steps in degrees / s.
        """
        tmp = self.therm.get_tmp()
        tmp_dif = np.abs(self.tmp_aim - tmp)
        if rate <= 0 and tmp_dif < 2. * rate:  # If cooling and close to aim tmp turn off.
            self.turn_off()
        elif rate > 0 and tmp_dif < 2. * rate:  # If heating and close to aim tmp turn on.
            self.turn_on()
        elif tmp > self.tmp_aim and not self.on:
            self.turn_on()
        elif tmp < self.tmp_aim and self.on:
            self.turn_off()

    def energy_used(self, v, I):
        """
        Calculates the energy used by the power source. First calculates the power (P=IV) then multiplies this
        with the time taken to change the temperature by a known amount.
        :param v: (float) Power supply voltage.
        :param I: (float) Power supply current.
        :return: (float) The energy used if calculated, 0 otherwise.
        """
        if self.first_on and self.first_off:
            p = I * v
            t = self.final_time - self.init_time  # Total time the chip was on.
            energy_used = p * t
            return energy_used
        else:
            return 0

    def energy_water(self, mass, c=4186):
        """
        Calculates the energy requited to change the temperature of water by a given amount.
        :param mass: (float) Mass of substance in kJ.
        :param c: (float) Heat capacity of substance in KJ/kg/K.
        :return: (float) The energy required.
        """
        delta_tmp = self.first_on - self.first_off
        cooling_energy = c * mass * delta_tmp
        print("delta_tmp: %.2f, mass: %.2f, c: %.2f." %(delta_tmp, mass, c))
        return cooling_energy

    def efficiency(self, mass, v, i):
        """
        Calculates the efficency of the cooling system by comparing the energy used by the power source to the energy
        needed to change the temperature of the substance by the changes amount.
        :param mass: (float) Mass of substance kg.
        :param v: (float) Voltage of power source.
        :param i: (float) Current of power source.
        :return: Fractional efficiency if calculated and false otherwise.
        """
        if self.first_on and self.first_off and not self.eff_calced:
            # Only calculates between the first time the chip is turned on and the first time the chip is turned
            # of (reaches aim temperature - precision)
            self.eff_calced = True
            eff = self.energy_water(mass) / self.energy_used(v, i)
            print("The efficiency of the refrigerator is: %.2f %%." %(eff*100))
            return eff
        else:
            return False
