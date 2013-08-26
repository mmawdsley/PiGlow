#!/usr/bin/env python
# -*- coding: utf-8 -*-

from piglow import PiGlow
from time import sleep

class Alert:

  def __init__ (self, piglow):

    self.piglow = piglow
    self.val_range = [2, 5, 9, 5, 2]
    self.delay = 0.04
    self.arm_count = 3
    self.arm_length = 6
    self.frames = []
    self.calc_frames ()


  def show (self, times=None):
    """Runs the alert the given number of times"""

    try:
      times = int (times)
    except:
      times = 1

    for i in range (0, times):
      self.run ()

    self.clear ()


  def run (self):
    """Runs the alert"""

    for frame in self.frames:
      self.show_frame (frame)
      sleep (self.delay)


  def show_frame (self, frame):
    """Shows a frame"""

    values = [0, 0, 0, 0, 0, 0]

    for i in range (0, len (values)):
      try:
        values[i] = frame[i]
      except IndexError:
        values[i] = 0

    for arm in range (0, self.arm_count):
      self.piglow.arm (arm + 1, values)


  def clear (self):
    """Clears the LEDs"""

    self.piglow.all (0)


  def calc_frames (self):
    """Calculates the frames for an alert"""

    self.frames = []

    i = 1
    add = 1

    while i > -1:
      val_range = self.val_range
      vals = []

      for j in range (0, i):

        try:
          vals.append (val_range[j])
        except IndexError:
          vals.append (0)

      new_vals = []

      for j in reversed (vals):
        new_vals.append (j)

      self.frames.append (new_vals)

      try:

        if add == -1 and new_vals == [min (self.val_range)]:
          break

      except IndexError:
        pass

      try:

        if new_vals[self.arm_length - 1] == max (self.val_range):
          add = -1

      except IndexError:
        pass

      i = i + add


if __name__ == "__main__":

  times = 3
  piglow = PiGlow ()
  alert = Alert (piglow)

  try:
    alert.show (times)
  except KeyboardInterrupt:
    alert.clear ()
