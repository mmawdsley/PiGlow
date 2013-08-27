## PiGlow-Status

Daemon for illustrating the current status of your Raspberry Pi using
@boeeerb's PiGlow class.


## Requirements

    sudo apt-get install python-smbus
    sudo apt-get install python-psutil


## Setup

Create two symlinks to piglow_status.py in /sbin:

    sudo ln -s /home/USERNAME/piglow-status/piglow_status.py /sbin/piglow_status_server
    sudo ln -s /home/USERNAME/piglow-status/piglow_status.py /sbin/piglow_status_client


Then copy the configuration file to /etc/piglow_status.conf and
assuming that you have all the libraries available you should be able
to start the server:

    sudo /sbin/piglow_status_server


If the PiGlow doesn't light up you can start it with this command
which won't run in the background so you can see any errors it spits
out:

    sudo /sbin/piglow_status_server start


Once it's running it'll start displaying the time in binary, and you
can start sending it commands:

    sudo /sbin/piglow_status_client alert 3
    sudo /sbin/piglow_status_client off
    sudo /sbin/piglow_status_client clock
    sudo /sbin/piglow_status_client cycle medium
    sudo /sbin/piglow_status_client unlock

The client script doesn't *require* root access unless it cannot
connect to the server, in which case it'll attempt to start it for you
before passing your command along.


## One-off Jobs

 - "alert [n]" runs the alert animation the given number of times
 - "off" disables the current idle animation
 - "unlock" stops the current looping animation

## Idle Jobs

Idle functions are ran when there are no jobs to perform. There can
only be one idle function at a time.

 - "clock" binary clock animation by @boeeerb


## Looping Jobs

Looping jobs run continuously until stopped. Other functions are still
added to the list, but won't be ran until the looping function has
finished.

 - cycle [slow|medium|fast] runs a looping animation at the given speed

Looping jobs extend the Status_Locking class so they can be easily
started and stopped by the server.


## Ideas for things to be notified of

### apt-get

```
DPkg::Pre-Invoke {"/sbin/piglow_status_client cycle medium";};
DPkg::Post-Invoke {"/sbin/piglow_status_client unlock";};
```
* /etc/apt/apt.conf.d/99piglowstatus


### Transmission Downloads

```
"script-torrent-done-enabled": true,
"script-torrent-done-filename": "/sbin/piglow_status_client alert 3",
```
* /etc/transmission-daemon/settings.json
