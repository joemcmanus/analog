#!/usr/bin/env python
# File    : analog.py 
# Author  : Joe McManus josephmc@alumni.cmu.edu
# Version : 0.1  12/20/2015
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

parser = argparse.ArgumentParser(description='Analog Pin Value Reader for Galileo')
parser.add_argument('pinNumber', help="Specify the analog pin number, i.e. 0-5", type=int)
parser.add_argument('--temperature', help="Change to a temperature value for TMP36", action="store_true")
parser.add_argument('--version', action='version',version='%(prog)s 0.1')
args=parser.parse_args()


try: 
	#Initialize the MRAA pin
	pin = mraa.Aio(int(args.pinNumber)) 
	#Set it to a 12 bit value, change to 10 for Galileo gen1
	pin.setBit(12)
except Exception,e:
	print("Error: {:s}". format(e))
	sys.exit()

while 1: 
	try:
		table = PrettyTable(["Data Type", "Value"])
		rawReading = pin.read()
		table.add_row(["Raw MRAA Reading", rawReading])
		
		#Galileo voltage should be the raw reading divided by 819.0
		#The reading is from 0-4095 to cover 0-5 volts
		#Or 4095/5=819.0
		galVoltage=float(rawReading / 819.0)
		table.add_row(["MRAA Voltage Calc", round(galVoltage, 4)])

		#Access the raw voltage reading
		path="/sys/bus/iio/devices/iio:device0/in_voltage" + str(args.pinNumber) + "_raw"
		sysRaw =subprocess.check_output(['/bin/cat', path], stderr=subprocess.STDOUT)
		table.add_row(["sys/bus/iio Raw Reading", sysRaw.strip()])

		#The raw voltage reading needs to be multiplied by the scale, get the scale
		path="/sys/bus/iio/devices/iio:device0/in_voltage" + str(args.pinNumber) + "_scale"
		sysScale=subprocess.check_output(['/bin/cat', path ], stderr=subprocess.STDOUT)
		sysScale=float(sysScale.strip())	
		table.add_row(["/sys/bus/iio scale", round(sysScale, 4)])

		table.add_row(["sys/bus/iio MV calculated ", round(float(sysRaw) * sysScale)])

		if args.temperature:
			tempC= (galVoltage *100 ) - 50 
			table.add_row(["Celsius", round(tempC, 2)])

			tempF= (tempC * 9.0 / 5.0) + 32.0
			table.add_row(["Fahrenheit", round(tempF, 2)])

		table.add_row(["Time", time.strftime("%Y/%m/%d %H:%M:%S")])
		print(table)

		time.sleep(10)
		print("")

	except KeyboardInterrupt:
		sys.exit()

	except Exception,e: 
		print("Error: {:s}". format(e))
		sys.exit()
