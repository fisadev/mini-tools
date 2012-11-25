#!/usr/bin/python
import datetime
import os
import time
import sys


while True:
    os.system('clear')
    input_time = raw_input('t: ')
    if not input_time:
        os.system('clear')
        sys.exit()

    start = datetime.datetime.now()

    if ':' in input_time:
        minutes, seconds = map(float, input_time.split(':'))
    else:
        minutes, seconds = float(input_time), 0
    total_seconds = minutes * 60.0 + seconds + 1
    total_time = datetime.timedelta(0, total_seconds, 0)

    try:
        while datetime.datetime.now() - start < total_time:
            os.system('clear')
            left = total_time - (datetime.datetime.now() - start)
            print ' %02i:%02i' % (left.seconds / 60, left.seconds % 60)
            time.sleep(0.5)

        os.system('clear')
        print 'time!'
    except KeyboardInterrupt:
        os.system('clear')
        print 'stop'
    raw_input()
