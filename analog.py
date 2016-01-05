#!/usr/bin/env python
# File    : analog.py 
# Author  : Joe McManus josephmc@alumni.cmu.edu
# Version : 0.3  01/04/2016
# Copyright (C) 2015 Joe McManus
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import sys 
import mraa
import time
import subprocess
import argparse
from prettytable import PrettyTable
import re

parser = argparse.ArgumentParser(description='Analog Pin Value Reader for Galileo')
parser.add_argument('pinNumber', help="Specify the analog pin number, i.e. 0-5", type=int)
parser.add_argument('--temperature', help="Change to a temperature value for TMP36", action="store_true")
parser.add_argument('--count', help="Number of times to execute, default infinity", default=0, type=int, action="store")
parser.add_argument('--delay', help="Number of seconds to wait between readings, default 10", default=10, type=int, action="store")
parser.add_argument('--version', action='version',version='%(prog)s 0.3')
args=parser.parse_args()

def checkAnalogPin(pin):
	#First lets check to see if the 22K pull up resister is set on Pin 0 
	#See bug report: https://github.com/intel-iot-devkit/mraa/issues/390
	fixGpio=subprocess.check_output(['/bin/cat', '/sys/kernel/debug/gpio'], stderr=subprocess.STDOUT)
	gpio49=re.search(r'gpio-49.*', fixGpio)                                                          
	if hasattr(gpio49, 'group'):                                                                     
		status=str(gpio49.group(0)).split()                                                      
		#If it is set to in exit
		if status[3] == "in":
			return
		else:
			print("Pull up resister set to hi, attempting to change.")
			fh=open("/sys/class/gpio/gpio49/direction", "w")
			fh.write('in')
			fh.close()
			#For some reason it does not update until you read, so lets read
			pin.read()

	fixGpio=subprocess.check_output(['/bin/cat', '/sys/kernel/debug/gpio'], stderr=subprocess.STDOUT)
	gpio49=re.search(r'gpio-49.*', fixGpio)                                                          
	if hasattr(gpio49, 'group'):                                                                     
		status=str(gpio49.group(0)).split()                                                      
		if status[3] == "out":
			print("Still showing as output, this will cause bad readings.")
try: 
	#Initialize the MRAA pin
	pin = mraa.Aio(int(args.pinNumber)) 
	#Set it to a 12 bit value
	pin.setBit(12)
except Exception,e:
	print("Error: {:s}". format(e))
	sys.exit()

i = 0
while True:
	try:
		table = PrettyTable(["Data Type", "Value"])

		#Analog 0 defaults to high and output, check for this
		if args.pinNumber == 0:
			checkAnalogPin(pin)
			
		rawReading = pin.read()
		table.add_row(["Raw MRAA Reading", rawReading])
		
		#Galileo voltage should be the raw reading divided by 819.0
		#The reading is from 0-4095 to cover 0-5 volts
		#Or 4095/5=819.0
		galVoltage=float(rawReading / 819.0)
		table.add_row(["MRAA Voltage Calc", round(galVoltage, 3)])

		#Access the raw voltage reading
		path="/sys/bus/iio/devices/iio:device0/in_voltage" + str(args.pinNumber) + "_raw"
		sysRaw =subprocess.check_output(['/bin/cat', path], stderr=subprocess.STDOUT)
		table.add_row(["sys/bus/iio Raw Reading", sysRaw.strip()])

		#The raw voltage reading needs to be multiplied by the scale, get the scale
		path="/sys/bus/iio/devices/iio:device0/in_voltage" + str(args.pinNumber) + "_scale"
		sysScale=subprocess.check_output(['/bin/cat', path ], stderr=subprocess.STDOUT)
		sysScale=float(sysScale.strip())	
		table.add_row(["/sys/bus/iio scale", round(sysScale, 4)])

		table.add_row(["sys/bus/iio Voltage Calc ", round((float(sysRaw) * sysScale / 1000),3 )])

		if args.temperature:
			tempC= (galVoltage *100 ) - 50 
			table.add_row(["Celsius", round(tempC, 2)])

			tempF= (tempC * 9.0 / 5.0) + 32.0
			table.add_row(["Fahrenheit", round(tempF, 2)])

		table.add_row(["Time", time.strftime("%Y/%m/%d %H:%M:%S")])
		print(table)
		print("")

		if args.count != 0:
			i = i+1
			if args.count == i:
				break

		time.sleep(args.delay)

	except KeyboardInterrupt:
		sys.exit()

	except Exception,e: 
		print("Error: {:s}". format(e))
		sys.exit()
