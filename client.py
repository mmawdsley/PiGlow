#!/usr/bin/env python
# -*- coding: utf-8 -*-

from socket import *
import os
import sys
import inspect
import config as cfg
from time import sleep

class PiGlow_Status_Client:

  def __init__ (self):

    self.cfg = cfg
    self.address = (self.cfg.HOST, self.cfg.PORT)


  def main (self, args):
    """Reads instructions from the command line and passes them along to the server"""

    self.run (" ".join (args))


  def run (self, command):
    """Sends a command to the server"""

    if self.send_command (command) == True:
      return

    self.spawn_server ()
    self.send_command (command)


  def spawn_server (self):
    """Attempts to spawn the server as a separate process"""

    cwd = os.path.dirname (os.path.abspath (inspect.getfile (inspect.currentframe ())))
    server = "%s/server.py" % cwd
    os.spawnl (os.P_NOWAIT, server, server, "start")
    sleep (2)


  def send_command (self, command):
    """Sends a command to the server"""

    try:

      sock = socket ()
      sock.connect (self.address)
      sock.send (command)
      sock.close ()

      return True

    except Exception:

      return False


if __name__ == "__main__":

  client = PiGlow_Status_Client ()
  client.main (sys.argv[1:])
