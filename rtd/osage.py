import argparse
import datetime
import sqlite3
import sys

def main():
    now_dt = datetime.datetime.now()
    day_number = int(now_dt.strftime('%w'))
    day = convert_day(day_number)
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
    parser.add_argument(
        '--all',
        action = 'store_true',
        default = False,
        dest = 'output_all',
        help = 'output a CSV format of all possible times')

    args = parser.parse_args()
    current_time = convert_time(args.time)
    output_all = args.output_all
    
    try:
        # TODO: clean-up data access
        # TODO: write a class with methods to set class variables to hold query results
        # TODO: loop through a set of potential times, and generate a class for each query set
        # TODO: for each class instance, determine average sprint times
        # TODO: graph the data to show best times to sprint; find maximum sprint distance and locate gains
        db_connection = sqlite3.connect('rtd.db')
        cursor = db_connection.cursor()
       
        if output_all:
            cursor.execute("DROP TABLE IF EXISTS stats")
            cursor.execute("CREATE TABLE stats(current_time INT, day TEXT, sprint_time INT, sprint_travel_time INT, sprint_min_speed REAL, connect_travel_time INT, time_saved INT)")

            for day_number in [1, 5, 6, 0]:
                for hour in range(0, 23):
                    for minute in range(0, 59):
                        current_time = (hour * 100) + minute
                        day = convert_day(day_number)
                        compute_verdict(current_time, day, cursor, False)
                        db_connection.commit()
        else:
            compute_verdict(current_time, day, cursor, True)
            
    except sqlite3.Error, e:
        print e
        sys.exit(1) 
    finally:
        db_connection.close()

def compute_verdict(current_time, day, cursor, output):
        query = "SELECT * FROM schedule WHERE route = 'W' AND day = '" + day + "' AND depart_time > " + str(current_time) + " AND arrive_time IS NOT NULL ORDER BY depart_time ASC"
        #if output: print query
        cursor.execute(query)
        result = cursor.fetchone()
        #if output: print result
        next_west_depart_time = result[3]
        next_west_arrive_time = result[4]

        sprint_time = subtract_time(next_west_depart_time, current_time)
        sprint_travel_time = travel_time(current_time, next_west_arrive_time)
        sprint_min_speed = sprint_speed(0.9, sprint_time)

        query = "SELECT * FROM schedule WHERE route in ('C','E') AND day = '" + day + "' AND depart_time >= " + str(current_time) + " AND arrive_time IS NOT NULL ORDER BY depart_time ASC"
        if output: print query
        cursor.execute(query)
        result = cursor.fetchone()
        if output: print result

        # connecting train leaves 10th/Osage
        next_connection_depart_time = result[3]
        # connecting train arrives at Auraria West
        next_connection_arrive_time = result[4]

        query = "SELECT * FROM schedule WHERE route = 'W' AND day = '" + day + "' AND depart_time >= " + str(next_connection_arrive_time) + " AND arrive_time IS NOT NULL ORDER BY depart_time ASC"
        #if output: print query

        cursor.execute(query)
        result = cursor.fetchone()

        if result is None:
            query = "SELECT * FROM schedule WHERE route = 'W' and day = '" + day + "' AND depart_time >= 0 AND arrive_time IS NOT NULL ORDER BY depart_time ASC"
            #if output: print query
            cursor.execute(query)
            result = cursor.fetchone()
            
        next_connecting_west_depart_time = result[3]
        next_connecting_west_arrive_time = result[4]

        connect_travel_time = travel_time(current_time, next_connecting_west_arrive_time)
        # both are in minutes
        time_saved = connect_travel_time - sprint_travel_time

        if output:
            print 'current_time = %d' % current_time
            print 'next_west_depart_time = %d' % next_west_depart_time
            print 'next_west_arrive_time = %d' % next_west_arrive_time
            print '-- time to sprint = %d minutes' % sprint_time
            print '-- travel time if you sprint = %d minutes' % sprint_travel_time
            print '-- minimum sprint speed = %d mph' % sprint_min_speed
            print 'next_connection_depart_time = %d' % next_connection_depart_time
            print 'next_connection_arrive_time = %d' % next_connection_arrive_time
            if next_connecting_west_depart_time is not None:
                print 'next_connecting_west_depart_time = %d' % next_connecting_west_depart_time
            if next_connecting_west_arrive_time is not None:
                print 'next_connecting_west_arrive_time = %d' % next_connecting_west_arrive_time
            if connect_travel_time is not None:
                print '-- travel time if you connect = %d minutes' % connect_travel_time
            if time_saved is not None:
                print '-- time saved = %d minutes' % time_saved
            print '-- verdict: ' + sprint_check(sprint_min_speed, time_saved)
        else:
            print ','.join(map(str, [
                current_time, 
                day, 
                sprint_time, 
                sprint_travel_time, 
                sprint_min_speed, 
                connect_travel_time, 
                time_saved
            ]))

            query = "INSERT INTO stats VALUES (?, ?, ?, ?, ?, ?, ?)"
            cursor.execute(query, (current_time, day, sprint_time, sprint_travel_time, sprint_min_speed, connect_travel_time, time_saved))
            

# TODO: put in a common helper python module
def convert_day(number):
    if number == 0:
        return 'Sunday/Holiday'
    elif number == 5:
        return 'Friday'
    elif number == 6:
        return 'Saturday'
    else:
        return 'Monday-Thursday'

def convert_time(time):
    am_pm = time[len(time) - 1]
    time = time[:-1]
    if (am_pm == 'A'):
        if (len(time) == 4 and time[:2] == '12'):
            time = int(time) - 1200
    else:
        if (len(time) == 3 or (len(time) == 4 and time[:2] != '12')):
            time = 1200 + int(time)

    return int(time)

def travel_time(current_time, arrival_time):
    return subtract_time(arrival_time, current_time)

def sprint_time(speed, distance):
    return (distance / speed) * 60

def sprint_speed(distance, minutes):
    if minutes == 0:
        return None
    else:
        return (60 * distance) / minutes 

def sprint_check(speed, time_saved):
    if time_saved is None or speed is None:
        return "Doesn't reach Golden"
    elif speed <= 15 and time_saved > 5:
        return 'GO!'
    else:
        return 'Stay'

def subtract_time(a, b):
    #print 'a = %d, b = %d' % (a, b)
    a_hours = (a / 100) % 24
    #print 'a_hours = %d' % a_hours
    b_hours = (b / 100) % 24
    #print 'b_hours = %d' % b_hours
    hours = ((a / 100) % 24 - (b / 100) % 24) % 24
    #print 'hours = %d' % hours
    if (a % 100) % 60 - (b % 100) % 60 < 0: hours -= 1
    minutes = ((a % 100) % 60 - (b % 100) % 60) % 60
    #print 'minutes = %d' % minutes
    return ((a % 100) % 60 - (b % 100) % 60) % 60 + (hours * 60)

if __name__ == '__main__':
    main()

