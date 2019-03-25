#FILE: kWh.py
#NAME: Michael Edukonis
#DATE: MArch 24, 2019
#DESCRIPTION: kWh.py is a test program receiving output from arduino board connected to two 250 amp split core
#current transformers around the two main legs of a US residential electric supply.  Updates are received every
#two seconds and stored in mysql database on another machine for analysis and graphing. 

from serial import Serial
from datetime import datetime
from time import sleep
import time 
import os
import mysql.connector as mariadb

rate = 0.1059385        #from march 2019 electric bill
cost = 0.00
startTime = time.time()
start = datetime.now()
serial_port = Serial('COM5', 9600, timeout=0)
startingTime = start.strftime('%X')
startingDate = start.strftime('%m/%d/%Y')
mariadb_connection = mariadb.connect(host='', port='3306', user='', password='', database='electricity')
cursor = mariadb_connection.cursor()

while True:
        days, rem = divmod(time.time()-startTime, 86400)
        hours, rem = divmod(rem, 3600)
        minutes, seconds = divmod(rem, 60)
        if(serial_port.inWaiting()>0):
                sleep(.1)
                os.system('cls')
                t = datetime.now()
                line = serial_port.readline().decode('utf-8')
                measurement = line.split(',')
                stampTime = datetime.now()
                dateToStamp = stampTime.strftime('%Y-%m-%d')
                timeToStamp = stampTime.strftime('%X')
                measurement.append(dateToStamp)
                measurement.append(timeToStamp)
                
                #getting occassional bad measurement locking it up.
                #next two lines make sure that measurement[2] (the total kWh)
                #is a valid string that can be converted to a float i.e.
                #number, decimal point, number with no additional decimal
                #points that happened occasionally from a bad read over serial
        
                measTwo = measurement[2].split('.')             #split measurement[2] along it's decimal point[s]
                measurement[2] = measTwo[0] + '.' + measTwo[1]  #piece together only the integer part, decimal, and fractional part
                
                cost = float(measurement[2]) * rate
                print("Prog Start Time: " + "\t" + startingTime + "\t" + startingDate)
                print("Elapsed: " + "\t\tDays: {:0>2}\t{:0>2}:{:0>2}:{:02.0f}\n".format(int(days),int(hours),int(minutes),seconds))
                print("Measurement time stamp: " + measurement[3] + " " + measurement[4])
                print("Left: " + measurement[0] + "\t" + "Right: " + measurement[1] + "\t" + "kWh: " + measurement[2] + "\t" + "Cost: " + "{0:.3f}".format(cost))
                cursor.execute("INSERT INTO used (dt, time_now, left_side, right_side, cummulative) VALUES (%s,%s,%s,%s,%s)", (measurement[3],measurement[4],measurement[0], measurement[1], measurement[2]))
                mariadb_connection.commit()
mariadb_connection.close()
