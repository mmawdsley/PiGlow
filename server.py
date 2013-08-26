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
import thread
import time
import select
import os
import sys
import inspect
import config as cfg

class PiGlow_Status_Server:

  def __init__ (self):

    self.cfg = cfg
    self.idle_job = self.cfg.CMD_CLOCK
    self.jobs = []
    self.running = None
    self.quit = False
    self.locked_thread = None
    self.check_jobs_thread = None
    self.socket_manager_thread = None
    self.piglow = None
    self.clock = None
    self.alert = None
    self.in_progress = None
    self.job_interval = 0.1


  def main (self):
    """Creates the socket and starts the threads"""

    self.piglow = PiGlow ()
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

    while self.quit == False:
      pass

    self.exit ()


  def exit (self):
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
        self.quit = True
        break


      if self.locked_thread is None:
        # No currently locking jobs, we can process the next job in the list as
        # normal or run the idle task if none are scheduled
        self.run_jobs ()

      else:
        # A locking job is currently running, screen the job list for tasks
        # relating to it.
        self.check_locked_jobs ()

      time.sleep (self.job_interval)


  def quit_requested (self):
    """Returns true if the quit command is in the job list"""

    for job in self.jobs:

      if job[0] == self.cfg.CMD_QUIT:
        return True

    return False


  def check_locked_jobs (self):
    """Goes through the job list searching for tasks relating to the current locked job"""

    jobs = self.jobs
    self.jobs = []

    for job in jobs:

      if job[0] == self.cfg.CMD_CYCLE:

        try:
          self.in_progress.set_speed (job[1])
        except IndexError:
          pass

      elif job[0] == self.cfg.CMD_UNLOCK:
        self.unlock ()

      elif job[0] == self.cfg.CMD_OFF:
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

    if self.idle_job == self.cfg.CMD_CLOCK:
      self.clock.run ()


  def handle_job (self, job):
    """Performs the given job"""

    command = job[:1].pop ()
    args = job[1:]

    if command == self.cfg.CMD_QUIT:

      self.quit = True

    elif command == self.cfg.CMD_CYCLE:

      self.locked_thread = self.in_progress

      if len (args) > 0:
        self.in_progress.set_speed (args[0])

      self.in_progress.start ()

    elif command == self.cfg.CMD_ALERT:

      self.alert.show (*args)

    elif command == self.cfg.CMD_OFF:

      self.idle_job = None

    elif command == self.cfg.CMD_CLOCK:

      self.idle_job = self.cfg.CMD_CLOCK


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

    if command == self.cfg.CMD_CLOSE:
      clientsock.close ()
    else:
      self.jobs.append (command)


if __name__ == "__main__":

  try:

    if sys.argv[1] == "start":

      server = PiGlow_Status_Server ()
      server.main ()

  except IndexError:

    server_path = os.path.abspath (inspect.getfile (inspect.currentframe ()))
    os.spawnl (os.P_NOWAIT, server_path, server_path, "start")
