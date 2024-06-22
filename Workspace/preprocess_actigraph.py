# This script detects moments in which a user is sitting or lying but has a very high HR, and saves them in the dataset file
# It also cleans the rows where the HR value is under 50 or over 200

import os
import pandas as pd
import utilities.library as lib


def preprocessing(path, users, max_ibi_at_rest = 0):
    if max_ibi_at_rest == 0:
        print("Enter the maximum heart rate at rest (e.g. 100):")
        max_ibi_at_rest = int(input())
    print()     # extra line break that doesn't hurt

    # This list will contain the log rows that will be saved to the file
    result_text = ["Maximum heart rate entered: " + str(max_ibi_at_rest) + "\n\n"]
    
    for user in users:
        lib.logger(user, result_text)

        # Creating the dataframe
        df = pd.read_csv(path + '%s/%s.csv' %(user, "Actigraph"))
        df = df.drop(['Unnamed: 0'], axis=1, errors='ignore')  # Removing the index column
        df['day'] = df['day'].replace(-29, 2)  # Fix data for users 8 and 9


        # Removing rows with impossible HR values
        row_count = len(df)
        deleted_rows_count = len(df[df['HR'] > 200]) + len(df[df['HR'] < 50])
        df = df.drop(df[df['HR'] > 200].index)
        df = df.drop(df[df['HR'] < 50].index)
        df = df.reset_index(drop=True)
        lib.logger("Deleted rows: " + str(deleted_rows_count) + " out of " + str(row_count), result_text)
        

        # We are interested in users with an HR above the threshold when they are sitting or lying down
        cond_hr = df['HR'] > max_ibi_at_rest
        cond_incl_1 = df['Inclinometer Sitting'] == 1.0
        cond_incl_2 = df['Inclinometer Lying'] == 1.0
        filter_conditions = cond_hr & (cond_incl_1 | cond_incl_2)
        suspicious_rows = len(df[filter_conditions])

        rows_while_sitting_or_lying = len(df[cond_incl_1 | cond_incl_2].index)
        lib.logger("Rows spent sitting or lying down: " + str(rows_while_sitting_or_lying) + " out of " + str(len(df)), result_text, False)


        # Initializing new columns and cycle variables
        df["Checked"] = "No"
        df["Anomaly"] = False
        skip = False
        n_anomalies = 0

        # Iterate over the data filtered with the conditions to save only the cases where stress wasn't already present
        for idx, row in df[filter_conditions].iterrows():
            df.at[idx, "Checked"] = "Yes"
            if idx == 0:
                continue  # The first row has no previous one to compare with
            
            # Take data from the previous row, if the user was standing and still had a high HR, do not save:
            previous_row = df.loc[idx - 1]
            if (previous_row['Inclinometer Off'] == 1.0 or previous_row['Inclinometer Standing'] == 1.0):
                if (previous_row['HR'] < row["HR"] * 0.8):  # *0.8 to loosen the condition
                    df.at[idx, "Anomaly"] = True
                    n_anomalies += 1
                    skip = False
                else:
                    skip = True
            else:
                if (previous_row['HR'] <= max_ibi_at_rest):
                    skip = False
                    n_anomalies += 1
                    df.at[idx, "Anomaly"] = True
                elif not skip:
                    n_anomalies += 1
                    df.at[idx, "Anomaly"] = True
            

        if n_anomalies > 0:
            anomalies_percentage = round((n_anomalies / rows_while_sitting_or_lying) * 100, 2)
            lib.logger("Anomalies found: " + str(n_anomalies) + " out of " + str(suspicious_rows) + " possible", result_text)
            lib.logger("Percentage of time spent sitting or lying down: " + "{}%".format(anomalies_percentage) + "\n", result_text)
        else:
            lib.logger("No anomalies found out of {} possible\n".format(suspicious_rows), result_text)
        
        # Save the processed values to the new file
        user_file_name = path + user + "/Actigraph-processed.csv"
        df.round(3).to_csv(user_file_name)


    # Save the log
    os.makedirs(os.getcwd() + "/Outputs", exist_ok=True)
    with open(os.getcwd() + "/Outputs/Actigraph Preprocessing Results.txt", "w") as f:
        for row in result_text:
            f.write(row)

    print("Done! The results have been saved in the output file.")



if __name__=="__main__":
    path, users = lib.get_path_and_users("Actigraph")
    preprocessing(path, users)
