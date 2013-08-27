#!/usr/bin/env python
# -*- coding: utf-8 -*-

from piglow import PiGlow
from time import sleep
from threading import Thread
from status_locking import Status_Locking

class In_Progress (Status_Locking):

  def __init__ (self, piglow):

    self.piglow = piglow
    self.running = False
    self.thread = None
    self.speed = {
      "slow" : 0.06,
      "medium" : 0.03,
      "fast" : 0.015
    }
    self.delay = self.speed["medium"]


  def set_speed (self, speed):
    """Sets the speed"""

    try:
      self.delay = self.speed[speed]
    except IndexError:
      pass


  def start (self):
    """Starts the animation"""

    self.running = True

    if self.thread == None:
      self.thread = Thread (None, self.run, None, ())
      self.thread.start ()


  def stop (self):
    """Stops the animation"""

    self.running = False
    self.thread.join ()
    self.thread = None


  def run (self):
    """Performs the animation"""

    val = 2
    colour = 1

    self.piglow.all (0)

    while self.running == True:

      if colour == 19:
        colour = 1

        if val == 2:
          val = 0
        else:
          val = 2

      self.piglow.led (colour, val)
      sleep (self.delay)

      colour = colour + 1


if __name__ == "__main__":

  piglow = PiGlow ()
  in_progress = In_Progress (piglow)
  in_progress.set_speed ("medium")

  try:

    in_progress.start ()

    while True:
      sleep (1)

  except KeyboardInterrupt:

    in_progress.stop ()
    piglow.all (0)
