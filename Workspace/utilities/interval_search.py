# Script that searchs for temporal holes in the RR.csv files
# Holes are considered when longer than two seconds

import os
import sys
import pandas as pd
from datetime import datetime


def calculate_time_difference(start_time, end_time):
    """
    Calculate the difference in seconds between two times in 'hour:minute:second' format.

    Args:
        start_time: string with the start time in 'hour:minute:second' format.
        end_time: string with the end time in 'hour:minute:second' format.

    Returns:
        An integer with the difference in seconds between the two times.
    """

    # Convert strings to datetime objects
    start = datetime.strptime(start_time, "%H:%M:%S.%f")
    end = datetime.strptime(end_time, "%H:%M:%S.%f")

    # Calculate the difference between the two times
    difference = end - start

    # Return the difference in seconds
    return difference.total_seconds()


if __name__=="__main__":
    # Get the list of users
    path = os.getcwd() + '/DataPaper/'
    users = os.listdir(path)
    
    if ('.DS_Store') in users:
        users.remove(".DS_Store")

    # Create the txt file to store the analysis results
    file_txt = open("Outputs/RR-analysis.txt", "w")

    # For each user, retrieve and display the RR file gap statistics
    for user in users:
        print("Processing user:", user)
        # Read RR.csv
        try:
            df = pd.read_csv(os.path.join(path, user, 'RR.csv'))
        except Exception as e:
            print(e)
            print("Error reading csv file")
            sys.exit()

        num_intervals = 0
        num_intervals_10sec = 0
        num_intervals_20sec = 0
        num_intervals_30sec = 0
        interpolable_interval_seconds = 0

        # Read rows one by one to find gaps
        i = 0
        while i < len(df)-1:
            time1 = df.iloc[i]["time"]
            time2 = df.iloc[i+1]["time"]
            
            # Calculate the time difference in seconds
            time_gap = calculate_time_difference(time2, time1)
            
            # If the difference is greater than two seconds, count it as a gap
            if abs(time_gap) > 2:
                num_intervals += 1

            if abs(time_gap) > 2 and abs(time_gap) < 10:
                interpolable_interval_seconds += abs(time_gap)

            if abs(time_gap) >= 10:
                num_intervals_10sec += 1
            if abs(time_gap) >= 20:
                num_intervals_20sec += 1
            if abs(time_gap) >= 30:
                num_intervals_30sec += 1

            i += 1

        # Write these statistics to a txt file
        file_txt.write("User statistics: " + user)
        file_txt.write("\nSignificant gaps found: " + str(num_intervals))
        file_txt.write("\nIntervals greater than or equal to 10 seconds: " + str(num_intervals_10sec))
        file_txt.write("\nIntervals greater than or equal to 20 seconds: " + str(num_intervals_20sec))
        file_txt.write("\nIntervals greater than or equal to 30 seconds: " + str(num_intervals_30sec))
        file_txt.write("\nTotal interpolable seconds: " + str(interpolable_interval_seconds))
        file_txt.write("\nTotal interpolable seconds in hours: " + str(interpolable_interval_seconds/60/60))
        file_txt.write("\n\n")
        
    # Close the txt file
    file_txt.close()
