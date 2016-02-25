# analog.py
A python script to read analog values on the Intel Galileo 

The Intel Galileo is a great device for tinkering with the IoT. After tinkering with it for a bit I was unable to find a working example of reading an analog sensor with the linux side of the Galileo. 

This imports the MRAA library and converts the reading to volts. As a sanity check it also reads the files in /sys/bus/iio/devices/iio:device0/in_voltage 

    usage: analog.py [-h] [--temperature] [--count COUNT] [--version] pinNumber
 
    Analog Pin Value Reader for Galileo

    positional arguments:
       pinNumber      Specify the analog pin number, i.e. 0-5

    optional arguments:
      -h, --help     show this help message and exit
      --temperature  Print a temperature value for TMP36
      --count COUNT  Number of times to execute, default infinity
      --delay DELAY  Number of seconds to wait between readings, default 10
      --quiet        Quiet display, show only the voltage of the analog pin
      --version      show program's version number and exit


This example shows reading an analog sensor (TMP36) on A0. 

    root@galileo:~# ./analog.py 0
    +---------------------------+---------------------+
    |         Data Type         |        Value        |
    +---------------------------+---------------------+
    |      Raw MRAA Reading     |         568         |
    |     MRAA Voltage Calc     |        0.694        |
    |  sys/bus/iio Raw Reading  |         580         |
    |     /sys/bus/iio scale    |        1.2207       |
    | sys/bus/iio Voltage Calc  |        0.708        |
    |            Time           | 2015/12/21 06:38:18 |
    +---------------------------+---------------------+

If you have a TMP36 temperature sensor you can pass --temperature in on the command line to display the calculated temperature. 

    root@galileo:~# ./analog.py 1 --temperature
    +---------------------------+---------------------+
    |         Data Type         |        Value        |
    +---------------------------+---------------------+
    |      Raw MRAA Reading     |         568         |
    |     MRAA Voltage Calc     |        0.694        |
    |  sys/bus/iio Raw Reading  |         568         |
    |     /sys/bus/iio scale    |        1.2207       |
    | sys/bus/iio Voltage Calc  |        0.693        |
    |          Celsius          |        19.35        |
    |         Fahrenheit        |        66.84        |
    |            Time           | 2016/01/05 04:42:11 |
    +---------------------------+---------------------+

To run it 5 times on A0 with a delay of 1 second and show the temperature.
 
    root@galileo2:~# ./analog.py 0 --count 5 --delay 1  --temperature 
    Pull up resister set to hi, attempting to change.
    +---------------------------+---------------------+
    |         Data Type         |        Value        |
    +---------------------------+---------------------+
    |      Raw MRAA Reading     |         568         |
    |     MRAA Voltage Calc     |        0.694        |
    |  sys/bus/iio Raw Reading  |         580         |
    |     /sys/bus/iio scale    |        1.2207       |
    | sys/bus/iio Voltage Calc  |        0.708        |
    |          Celsius          |        19.35        |
    |         Fahrenheit        |        66.84        |
    |            Time           | 2016/01/05 04:47:31 |
    +---------------------------+---------------------+

To only display the voltage of A1 and exit. 

    root@galileo2:~# ./analog.py 1 --quiet --count=1
    0.694

There is a prerequisite of installing the module PrettyTable. If you have not installed PIP, follow these instructions.

    curl https://bootstrap.pypa.io/ez_setup.py -o ez_seetup.py
    python ez_setup.py --insecure
    
Then you must install PIP.

    curl  https://pypi.python.org/packages/source/p/pip/pip-8.0.2.tar.gz -o pip-8.0.2.tar.gz
    tar -zxvf pip-8.0.2.tar.gz
    cd pip-8.0.2
    python setup.py build install

Install PrettyTable

    pip install PrettyTable

Download the script and make it executable. 

    curl https://raw.githubusercontent.com/joemcmanus/analog/master/analog.py -o analog.py
    chmod 755 analog.py


Wiring the TMP36
![alt tag](https://raw.githubusercontent.com/joemcmanus/lcd/master/GalileoGen2-TMP36_bb.png)


   
