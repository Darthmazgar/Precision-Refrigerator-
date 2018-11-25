"""
Unbused class which gives an outline to power a fan
to aid in cooling.
"""

import time


class Fan(object):
    # TODO Practically work out how to power this and get it running as an additional bonus.
    def __init__(self):
        self.on_time = 0
        self.total_on_time = 0
        self.on = False

    def turn_on(self):
        self.on_time = time.time()
        self.on = True
        pass

    def turn_off(self):
        self.total_on_time += time.time() - self.on_time
        self.on = False

    def get_total_on_time(self):
        if self.on:
            return self.total_on_time + (time.time() - self.on_time)
        else:
            return self.total_on_time
