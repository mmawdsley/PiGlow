#!/usr/bin/env python
# -*- coding: utf-8 -*-

from clock import Clock
from alert import Alert
from inprogress import In_Progress
from piglow import PiGlow
from time import sleep
from datetime import datetime
from socket import *
from threading import Thread
import ConfigParser
import errno
import thread
import select
import os
import sys
import inspect

class PiGlow_Status_Config:

  def __init__ (self):

    self.config_path = "/etc/piglow_status.conf"

    config = ConfigParser.ConfigParser ()
    config.read (self.config_path)

    self.TIMEOUT = config.getint ("main", "timeout")
    self.BUFF = config.getint ("main", "buff")
    self.HOST = config.get ("main", "host")
    self.PORT = config.getint ("main", "port")


class PiGlow_Status_Commands:

  def __init__ (self):

    self.ALERT = "alert"
    self.CLOCK = "clock"
    self.CLOSE = "close"
    self.CYCLE = "cycle"
    self.OFF = "off"
    self.QUIT = "quit"
    self.UNLOCK = "unlock"


class PiGlow_Status_Server:

  def __init__ (self):

    self.cfg = PiGlow_Status_Config ()
    self.commands = PiGlow_Status_Commands ()
    self.idle_job = self.commands.CLOCK
    self.jobs = []
    self.running = None
    self.locked_thread = None
    self.check_jobs_thread = None
    self.socket_manager_thread = None
    self.piglow = None
    self.clock = None
    self.alert = None
    self.in_progress = None
    self.job_interval = 0.1


  def start (self):
    """Creates the socket and starts the threads"""

    try:
      self.piglow = PiGlow ()

    except IOError as e:

      if e[0] == errno.EACCES:
        print >> sys.stderr, "Permission denied, try running as root"
      else:
        print >> sys.stderr, "Unknown error accessing the PiGlow"

      sys.exit (1)

    self.piglow.all (0)

    self.clock = Clock (self.piglow)
    self.alert = Alert (self.piglow)
    self.in_progress = In_Progress (self.piglow)

    address = (self.cfg.HOST, self.cfg.PORT)

    serversock = socket (AF_INET, SOCK_STREAM)
    serversock.setsockopt (SOL_SOCKET, SO_REUSEADDR, 1)
    serversock.bind (address)
    serversock.listen (5)

    self.check_jobs_thread = Thread (None, self.check_jobs, None, ())
    self.socket_manager_thread = Thread (None, self.socket_manager, None, (serversock, ))

    self.start_threads ()

    while self.running == True:
      sleep (1)

    self.stop ()


  def stop (self):
    """Closes the threads and returns"""

    self.stop_threads ()
    self.piglow.all (0)


  def start_threads (self):
    """Starts the threads"""

    self.running = True

    self.check_jobs_thread.start ()
    self.socket_manager_thread.start ()


  def stop_threads (self):
    """Stops the threads"""

    self.running = False
    self.unlock ()

    self.check_jobs_thread.join ()
    self.socket_manager_thread.join ()


  def check_jobs (self):
    """Performs the actions in the job list"""

    while self.running == True:

      if self.quit_requested ():
        self.running = False
        break


      if self.locked_thread is None:
        # No currently locking jobs, we can process the next job in the list as
        # normal or run the idle task if none are scheduled
        self.run_jobs ()

      else:
        # A locking job is currently running, screen the job list for tasks
        # relating to it.
        self.check_locked_jobs ()

      sleep (self.job_interval)


  def quit_requested (self):
    """Returns true if the quit command is in the job list"""

    for job in self.jobs:

      if job[0] == self.commands.QUIT:
        return True

    return False


  def check_locked_jobs (self):
    """Goes through the job list searching for tasks relating to the current locked job"""

    jobs = self.jobs
    self.jobs = []

    for job in jobs:

      if job[0] == self.commands.CYCLE:

        try:
          self.in_progress.set_speed (job[1])
        except IndexError:
          pass

      elif job[0] == self.commands.UNLOCK:
        self.unlock ()

      elif job[0] == self.commands.OFF:
        self.unlock ()
        self.jobs.append (job)

      else:
        self.jobs.append (job)


  def run_jobs (self):
    """First the first job in the list or the current idle job"""

    if len (self.jobs) > 0:

      job = self.jobs[:1].pop ()
      self.jobs = self.jobs[1:]

      self.handle_job (job)

    else:

      if self.idle_job is not None:
        self.run_idle_job ()
      else:
        self.piglow.all (0)


  def run_idle_job (self):
    """Runs the current idle job"""

    if self.idle_job == self.commands.CLOCK:
      self.clock.run ()


  def handle_job (self, job):
    """Performs the given job"""

    command = job[:1].pop ()
    args = job[1:]

    if command == self.commands.QUIT:

      self.running = False

    elif command == self.commands.CYCLE:

      self.locked_thread = self.in_progress

      if len (args) > 0:
        self.in_progress.set_speed (args[0])

      self.in_progress.start ()

    elif command == self.commands.ALERT:

      self.alert.show (*args)

    elif command == self.commands.OFF:

      self.idle_job = None

    elif command == self.commands.CLOCK:

      self.idle_job = self.commands.CLOCK


  def unlock (self):
    """Stops the currently locking thread"""

    if self.locked_thread is None:
      return

    self.locked_thread.stop ()
    self.locked_thread = None


  def socket_manager (self, serversock):
    """Creates handlers for new data given to this process via the socket"""

    rlist = [serversock]
    wlist = []
    xlist = []

    while self.running == True:

      readable, writable, errored = select.select (rlist, wlist, xlist, self.cfg.TIMEOUT)

      for s in readable:

        if s is serversock:
          clientsock, addr = serversock.accept ()
          thread.start_new_thread (self.socket_buffer_handler, (clientsock, ))


  def socket_buffer_handler (self, clientsock):
    """Handles data in the socket buffer"""

    data = clientsock.recv (self.cfg.BUFF).rstrip ()
    command = data.split (" ")

    if command == self.commands.CLOSE:
      clientsock.close ()
    else:
      self.jobs.append (command)


class PiGlow_Status_Client:

  def __init__ (self):

    self.cfg = PiGlow_Status_Config ()
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

    server_path = "/sbin/piglow_status_server"
    os.spawnl (os.P_WAIT, server_path, server_path)
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

  try:

    filename = os.path.basename (sys.argv[0])

    if filename == "piglow_status_server":

      try:

        if sys.argv[1] == "start":

          try:
            server = PiGlow_Status_Server ()
            server.start ()

          except KeyboardInterrupt:
            server.stop ()

      except IndexError:

        server_path = "/sbin/piglow_status_server"

        command = "/usr/bin/nice"
        args = [command, "-n", "10", server_path, "start"]
        os.spawnv (os.P_NOWAIT, command, args)

    elif filename == "piglow_status_client":

      client = PiGlow_Status_Client ()
      client.main (sys.argv[1:])

  except IndexError:

    pass
