import argparse
import datetime
import sqlite3
import sys

def main():
    now_dt = datetime.datetime.now()
    day_number = int(now_dt.strftime('%w'))
    if day_number == 0:
        day = 'Sunday/Holiday'
    elif day_number == 5:
        day = 'Friday'
    elif day_number == 6:
        day = 'Saturday'
    else:
        day = 'Monday-Thursday'

    now_formatted = str(int(now_dt.strftime('%I%M'))) + now_dt.strftime('%p')[:1].upper()

    osage_description = '\
        wait for the next train?  pass in a time and see if you should wait on a connecting C/E train \
        to Auraria West station, or to sprint to the Auraria West station to catch the next W train in \
        time!'

    parser = argparse.ArgumentParser(description = osage_description)
    parser.add_argument(
        '--time', 
        action = 'store', 
        dest = 'time', 
        default = now_formatted, 
        help = 'the time you arrived at 10th and Osage station, ex. 935A or 645P')

    args = parser.parse_args()
    current_time = convert_time(args.time)
    # print current_time
    
    try:
        # TODO: clean-up data access
        # TODO: write a class with methods to set class variables to hold query results
        # TODO: loop through a set of potential times, and generate a class for each query set
        # TODO: for each class instance, determine average sprint times
        # TODO: graph the data to show best times to sprint; find maximum sprint distance and locate gains
        db_connection = sqlite3.connect('rtd.db')
        cursor = db_connection.cursor()

        cursor.execute("SELECT * FROM schedule WHERE route = 'W' AND day = '" + day + "' AND depart_time > " + str(current_time) + " AND arrive_time IS NOT NULL ORDER BY depart_time ASC")
        result = cursor.fetchone()
        next_west_depart_time = result[3]
        next_west_arrive_time = result[4]

        print 'current_time = %d' % current_time
        print 'next_west_depart_time = %d' % next_west_depart_time
        print 'next_west_arrive_time = %d' % next_west_arrive_time
        # TODO: write utility function to subtract modulo 60 min
        print '-- time to sprint = %d minutes' % (next_west_depart_time - current_time)

        cursor.execute("SELECT * FROM schedule WHERE route in ('C','E') AND day = '" + day + "' AND depart_time > " + str(current_time) + " ORDER BY depart_time ASC")
        result = cursor.fetchone()

        # connecting train leaves 10th/Osage
        next_connection_depart_time = result[3]
        # connecting train arrives at Auraria West
        next_connection_arrive_time = result[4]
        print 'next_connection_depart_time = %d' % next_connection_depart_time
        print 'next_connection_arrive_time = %d' % next_connection_arrive_time

        cursor.execute("SELECT * FROM schedule WHERE route = 'W' AND day = '" + day + "' AND depart_time >= " + str(next_connection_arrive_time) + " AND arrive_time IS NOT NULL ORDER BY depart_time ASC")
        result = cursor.fetchone()
        next_connecting_west_depart_time = result[3]
        next_connecting_west_arrive_time = result[4]
        print 'next_connecting_west_depart_time = %d' % next_connecting_west_depart_time
        print 'next_connecting_west_arrive_time = %d' % next_connecting_west_arrive_time

    except sqlite3.Error, e:
        print e
        sys.exit(1) 
    finally:
        db_connection.close()

# TODO: put in a common helper python module
def convert_time(time):
    am_pm = time[len(time) - 1]
    time = time[:-1]
    if (am_pm == 'A'):
        if (len(time) == 4 and time[:2] == '12'):
            time = int(time) - 1200
    else:
        if (time[:2] != '12'):
            time = 1200 + int(time)

    return int(time)

if __name__ == '__main__':
    main()
