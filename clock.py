#!/usr/bin/env python
# -*- coding: utf-8 -*-

######################################
## A binary clock using the PiGlow  ##
##                                  ##
##  Example by Jason - @Boeeerb     ##
######################################

from piglow import PiGlow
from time import sleep
from datetime import datetime

class Clock:

  def __init__ (self, piglow):

    self.piglow = piglow
    self.show12hr = 1
    self.ledbrightness = 1
    self.hourflash = 0

    self.hourarm = 1
    self.minutearm = 2
    self.secondarm = 3

  def run (self):
    """Sets the LEDs to indicate the current time"""

    hourcount = 0
    hourcurrent = 0

    time = datetime.now ().time ()
    hour, minute, second = str (time).split (":")
    second, micro = str (second).split (".")
    hour = int (hour)

    if self.show12hr == 1:
      if hour > 12:
        hour = hour - 12

    minute = int (minute)
    second = int (second)

    # Check if current hour is different and set ready to flash hour
    if hourcurrent != hour:
      hourcount = hour
      hourcurrent = hour

    self.piglow.arm (self.hourarm, self.get_arm_values (hour))
    self.piglow.arm (self.minutearm, self.get_arm_values (minute))
    self.piglow.arm (self.secondarm, self.get_arm_values (second))

    # Flash the white leds for the hour
    if hourcount != 0:
      sleep (0.5)

      if self.hourflash == 1:
        self.piglow.white (self.ledbrightness)

      if self.hourflash == 2:
        self.piglow.all (self.ledbrightness)

      sleep (0.5)
      hourcount = hourcount - 1

    else:
      sleep (0.1)


  def get_arm_values (self, number):
    """Returns the list of values for an arm in binary from a base-10 number"""

    binnumber = "%06d" % int (bin (number)[2:])
    values = []

    for i in range (0, 6):
      values.append (self.ledbrightness if binnumber[i] == "1" else 0)

    return values


if __name__ == "__main__":

  piglow = PiGlow ()
  clock = Clock (piglow)

  try:
    while True:
      clock.run ()
      sleep (0.1)
  except KeyboardInterrupt:
    piglow.all (0)
