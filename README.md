## PiGlow-Status

Daemon for illustrating the current status of your Raspberry Pi using
@boeeerb's PiGlow class.


## Usage

Send commands to the daemon with the client.py script:

    ./client.py alert 3
    ./client.py cycle slow
    ./client.py quit


## Requirements

    sudo apt-get install python-smbus
    sudo apt-get install python-psutil


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
