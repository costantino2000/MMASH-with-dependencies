# This script cleans and interpolates the temporal holes in the RR.csv files

import os
import pandas as pd
import numpy as np
from datetime import timedelta
import utilities.library as lib



def calc_sec_difference(start, end):
    difference = end - start
    return difference.total_seconds()
    

def add_time(time, ibi):
    new_time = time + timedelta(milliseconds=(ibi*1000))
    return new_time
    

def interpolation(row, time_start, ibi_start):
    time_end = row["time"]
    ibi_end = row["ibi_s"]
    day = row["day"]

    gap = abs(calc_sec_difference(time_start, time_end))
    
    ibi_avg = (ibi_start + ibi_end) / 2
    num_intervals = int(gap / ibi_avg)
    ibi_interpolated = np.linspace([ibi_start], [ibi_end], num_intervals)
    # Since the first ibi would be the same as the previous row, interpolate again starting from the second value
    if len(ibi_interpolated) > 1:  # to prevent crashing if it finds only one value
        ibi_interpolated = np.linspace(ibi_interpolated[1][0], [ibi_end], num_intervals)
    
    ibi_list = []
    time_list = []
    day_list = []
    time_interval = time_start
    
    for i in range(num_intervals):
        time_interval = add_time(time_interval, ibi_interpolated[i][0])
        ibi_list.append(ibi_interpolated[i][0])
        time_list.append(time_interval)
        # Since the day is not marked in the time column, it takes the execution day, so it needs to be checked this way
        if (time_start.day == time_interval.day):
            day_list.append(day)
        else:
            day_list.append(day + 1)
    
    row["ibi_s"] = ibi_list
    row["day"] = day_list
    row["time"] = time_list

    return row

def preprocessing(path, users):
    result_text = []
    print()  # empty print to separate from the first print
    for user in users:
        print("Data cleaning and interpolation for", user)
        lib.logger(user, result_text, False)

        print("Creating the dataframe...")
        df = pd.read_csv(path + '%s/%s.csv' %(user, "RR"))
        df = df.drop(['Unnamed: 0'], axis=1, errors='ignore')  # Drop the CSV index column if present

        # Convert types to object to be able to replace rows with interpolated ones later
        df['day'] = df['day'].replace(-29, 2).astype(object)  # Fix days for some users
        df["time"] = pd.to_datetime(df["time"], infer_datetime_format=True).astype(object)  # infer_datetime_format is not necessary but doesn't hurt
        df["ibi_s"] = df["ibi_s"].astype(object)

        # Filter intervals below 0.3 and above 2 seconds (so-called ectopic beats)
        deleted_rows_count = len(df[(df['ibi_s'] < 0.3)]) + len(df[(df['ibi_s'] > 2)])
        lib.logger("Deleted {} rows out of {}".format(deleted_rows_count, len(df)), result_text)
        df = df.drop(df[(df['ibi_s'] < 0.3) | (df['ibi_s'] > 2)].index).reset_index(drop=True)
        

        # Interpolation of intervals between 2 and 10 seconds
        
        # Find the indices of rows where interpolation is needed and mark them in a new dataset column
        condition_1 = (df['time'] - df['time'].shift()).dt.total_seconds() > 2
        condition_2 = (df['time'] - df['time'].shift()).dt.total_seconds() <= 10
        interpolate_conditions = condition_1 & condition_2
        df['interpolate'] = interpolate_conditions

        rows_before_interpolation = len(df)
        lib.logger("Rows to interpolate: {} out of {}".format(len(df[interpolate_conditions]), rows_before_interpolation), result_text)

        # Perform interpolation for all rows one by one
        for idx, row in df[interpolate_conditions].iterrows():
            previous_row = df.loc[idx - 1]
            # Take time and ibi from the previous row (if it was interpolated in the previous step, it will be in list format)
            time_start = previous_row["time"][-1] if isinstance(previous_row["time"], list) else previous_row["time"]
            ibi_start = previous_row["ibi_s"][-1] if isinstance(previous_row["ibi_s"], list) else previous_row["ibi_s"]
            interpolated_row = interpolation(row, time_start, ibi_start)
            df.loc[idx] = interpolated_row  # Replace the original row with the interpolated one

        df = df.apply(pd.Series.explode)  # Explode interpolated rows to have one row per list element
        lib.logger("Added {} rows, now there are {}\n".format(len(df) - rows_before_interpolation, len(df)), result_text)

        # Prune decimal places
        df["time"] = df["time"].apply(lambda x: x.strftime("%H:%M:%S.%f")[:-3])
        df["ibi_s"] = df["ibi_s"].astype(float).round(3)

        # Save the file with processed data
        user_file_name = path + user + "/RR-processed.csv"
        df.reset_index(drop=True).to_csv(user_file_name)


    # Save the log
    os.makedirs(os.getcwd() + "/Outputs", exist_ok=True)
    with open(os.getcwd() + "/Outputs/RR Preprocessing Results.txt", "w") as f:
        for row in result_text:
            f.write(row)

    print("Done! The results were saved in the output file.")



if __name__=="__main__":
    path, users = lib.get_path_and_users("RR")
    preprocessing(path, users)
