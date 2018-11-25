from webiopi.devices.sensor.onewiretemp import DS18B20  # Import thermometer libraries.
from webiopi.devices.sensor.onewiretemp import DS18S20
import sys
import pygame  # Pygame to recieve keyboard input.
# from pygame.locals import *
import RPi.GPIO as GPIO
from Cooler import Cooler
from Thermometer import Thermometer
from Fan import Fan


def wait():
    """
    Condition to wait for next input to restart the cooler after a manual switch off.
    """
    print("Waiting to restart. press 'c' to continue.")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.K_c:
                print("Continuing ... ")
                return False


def main():
    GPIO.setwarnings(False)  # Turn of warnings from GPIO.
    pygame.init()
    screen = pygame.display.set_mode((640, 480))  # Window to allow keyboard input.
    pygame.display.set_caption("Precision Refrigerator")
    tmp_aim = 21.40
    # tmp_aim = float(input("Enter the aim temperature: "))
    precision = 0.125  # 0.0625  # Degrees (tmp +/- precision)
    mass = 0.05  # Mass in kg
    v = 3.  # Supply voltage of current chip.
    i = 1.5  # Supply current of cooling chip.
    count = 0
    test_range = 75
    save_all_data = True

    room_tmp = Thermometer(DS18S20(slave="10-000802deb0fc"), GPIO=GPIO, name="room")
    water_tmp = Thermometer(DS18B20(slave="28-000006cb82c6"), GPIO=GPIO, name="water", tmp_aim=tmp_aim,
                            show=True, arr_len=test_range)
    cooler = Cooler(GPIO=GPIO, tmp_aim=tmp_aim, therm=water_tmp, tmp_amb=room_tmp, name="Peltier",
                    precision=precision, input_pin=24)
    print("Current aim temperature set to: %.2f degrees celicus." % (tmp_aim))
    print("Keyboard commands:\n    'o' = Turn on cooler.\n    'f' = Turn off cooler.\n    's' = Set aim temperature.\n"
          "    'p' = Set precision of cooler.\n    't' = Show current Temperature.\n    'r' = Show current room temperature.\n")

    while True:  # TODO Change to have a run function to leave main as a set up only once key input has been tested.
        for event in pygame.event.get():  # Receiving input to set the state
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_o:
                    cooler.turn_on()
                    print("Cooler manually turned on.")
                if event.key == pygame.K_f:
                    cooler.turn_off()
                    print("Cooler manually turned off.")
                    wait()  # If turned of then don't turn straight back on again.
                if event.key == pygame.K_s:
                    tmp = float(input("Set the aim temperature:"))
                    cooler.set_tmp_aim(tmp, pr=True)
                if event.key == pygame.K_p:
                    tmp = float(input("Set precision temperature range (i.e. +/- tmp):"))
                    cooler.set_precision(tmp, pr=True)
                if event.key == pygame.K_t:
                    water_tmp.print_tmp()
                if event.key == pygame.K_r:
                    room_tmp.print_tmp()
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Method operations:
        #   converge(), hysteretic_conv(), rate_limit_conv(), pre_empt_conv(rate)
        cooler.hysteretic_conv()
        water_tmp.plot_tmp(title="Temperature Varying with Time.", x_lab="Time Step",
                           y_lab="Temperature $^oC$", draw=False)
        if save_all_data:
            water_tmp.store_data()

        rate, avg_rate = water_tmp.convergence_rate()  # Calculates the rate of temperature change.
        water_tmp.plot_rate(title="Rate of Temperature Change.", x_lab="Time Step",
                            y_lab="Rate $^oC / s$", draw=True)

        eff = cooler.efficiency(mass, v, i)  # Calculates the efficiency of the cooling system.
        if eff or count > 0:  # Waits for temperature to settle around aim temperature.
            count += 1

        if count == test_range:  # When temperature settled calculate the convergence method score.
            method_score = water_tmp.conv_score(precision, start=0, stop=test_range)
            print("This convergence method kept the temperature within the desired level of precision %.2f%% of the time over the test range." % (method_score * 100))

main()
