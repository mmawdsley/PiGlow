#!/usr/bin/env python
# -*- coding: utf-8 -*-

######################################
## A binary clock using the PiGlow  ##
##                                  ##
##  Example by Jason - @Boeeerb     ##
######################################

from time import sleep
from datetime import datetime

class Clock:

  def __init__ (self, piglow):

    self.piglow = piglow
    self.show12hr = 1
    self.ledbrightness = 1
    self.hourflash = 0

    self.armtop = "h"
    self.armright = "m"
    self.armbottom = "s"

  def run (self):

    hourcount = 0
    hourcurrent = 0

    time = datetime.now ().time ()
    hour,min,sec = str (time).split (":")
    sec,micro = str (sec).split (".")
    hour = int (hour)

    if self.show12hr == 1:
      if hour > 12:
        hour = hour - 12

    min = int (min)
    sec = int (sec)

    binhour = "%06d" % int (bin (hour)[2:])
    binmin = "%06d" % int (bin (min)[2:])
    binsec = "%06d" % int (bin (sec)[2:])

    # Check if current hour is different and set ready to flash hour
    if hourcurrent != hour:
      hourcount = hour
      hourcurrent = hour

    if self.armbottom == "h":
      arm3 = list (binhour)
    elif self.armbottom == "m":
      arm3 = list (binmin)
    else:
      arm3 = list (binsec)

    led13 = self.ledbrightness if arm3[5] == "1" else 0
    self.piglow.led (13,led13)
    led14 = self.ledbrightness if arm3[4] == "1" else 0
    self.piglow.led (14,led14)
    led15 = self.ledbrightness if arm3[3] == "1" else 0
    self.piglow.led (15,led15)
    led16 = self.ledbrightness if arm3[2] == "1" else 0
    self.piglow.led (16,led16)
    led17 = self.ledbrightness if arm3[1] == "1" else 0
    self.piglow.led (17,led17)
    led18 = self.ledbrightness if arm3[0] == "1" else 0
    self.piglow.led (18,led18)

    if self.armright == "h":
      arm2 = list (binhour)
    elif self.armright == "m":
      arm2 = list (binmin)
    else:
      arm2 = list (binsec)

    led07 = self.ledbrightness if arm2[5] == "1" else 0
    self.piglow.led (7,led07)
    led08 = self.ledbrightness if arm2[4] == "1" else 0
    self.piglow.led (8,led08)
    led09 = self.ledbrightness if arm2[3] == "1" else 0
    self.piglow.led (9,led09)
    led10 = self.ledbrightness if arm2[2] == "1" else 0
    self.piglow.led (10,led10)
    led11 = self.ledbrightness if arm2[1] == "1" else 0
    self.piglow.led (11,led11)
    led12 = self.ledbrightness if arm2[0] == "1" else 0
    self.piglow.led (12,led12)

    if self.armtop == "h":
      arm1 = list (binhour)
    elif self.armtop == "m":
      arm1 = list (binmin)
    else:
      arm1 = list (binsec)

    led01 = self.ledbrightness if arm1[5] == "1" else 0
    self.piglow.led (1,led01)
    led02 = self.ledbrightness if arm1[4] == "1" else 0
    self.piglow.led (2,led02)
    led03 = self.ledbrightness if arm1[3] == "1" else 0
    self.piglow.led (3,led03)
    led04 = self.ledbrightness if arm1[2] == "1" else 0
    self.piglow.led (4,led04)
    led05 = self.ledbrightness if arm1[1] == "1" else 0
    self.piglow.led (5,led05)
    led06 = self.ledbrightness if arm1[0] == "1" else 0
    self.piglow.led (6,led06)
