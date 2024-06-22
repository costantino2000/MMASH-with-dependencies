# Script that extracts numerous sleep features from sleep, actigraph, and rr datasets

import os
import pandas as pd
from scipy.stats import kurtosis, skew, entropy


def get_feature_vectors(path_directory):
    # Initialize an empty list to contain the feature vectors
    feature_vectors = []

    # Loop through the user directories
    for root, dirs, files in os.walk(path_directory):
        for directory in dirs:
            # User 7 is not used by the train_set_v6, which is the only one that needs these features, user 11 did not complete the questionnaires
            if directory.startswith('user') and directory != 'user_11' and directory != 'user_7':
                # Create paths for the files
                sleep_file_path = os.path.join(path_directory, directory, "sleep.csv")
                questionnaire_file_path = os.path.join(path_directory, directory, "questionnaire.csv")
                rr_file_path = os.path.join(path_directory, directory, "RR.csv")
                actigraph_file_path = os.path.join(path_directory, directory, "Actigraph.csv")

                # Check if sleep.csv, questionnaire.csv, and RR.csv files exist in the user folder
                if os.path.exists(sleep_file_path) and os.path.exists(questionnaire_file_path) and os.path.exists(rr_file_path) and os.path.exists(actigraph_file_path):
                    print("Processing", directory)

                    df_sleep = pd.read_csv(sleep_file_path)
                    df_questionnaire = pd.read_csv(questionnaire_file_path)
                    df_rr = pd.read_csv(rr_file_path)
                    df_actigraph = pd.read_csv(actigraph_file_path)

                    # DATA CORRECTION
                    df_rr = df_rr.drop(df_rr[(df_rr['ibi_s'] > 3)].index).reset_index(drop=True)  # Removes rows with ibi above 3 seconds in rr data
                    df_rr['day'] = df_rr['day'].replace(-29, 2)  # Fix data for users 8 and 9
                    df_actigraph['day'] = df_actigraph['day'].replace(-29, 2)  # Fix data for users 8 and 9

                    # WORKING ON df_sleep DATAFRAME
                    # Select the desired columns from the sleep.csv file
                    selected_sleep_columns = ['In Bed Time', 'Out Bed Time', 'Onset Time', 'Latency', 'Total Sleep Time (TST)',
                                    'Total Minutes in Bed', 'Efficiency', 'Wake After Sleep Onset (WASO)',
                                    'Number of Awakenings', 'Average Awakening Length', 'Movement Index',
                                    'Fragmentation Index', 'Sleep Fragmentation Index']

                    # Extract the first row as a feature vector from the sleep.csv file
                    feature_vector_sleep = df_sleep[selected_sleep_columns].iloc[0]

                    # User 1 has two rows unlike other users
                    if (directory == "user_1"):
                        feature_vector_sleep['Out Bed Time'] = df_sleep['Out Bed Time'].iloc[1]
                        feature_vector_sleep['Total Sleep Time (TST)'] = df_sleep['Total Sleep Time (TST)'].sum()
                        feature_vector_sleep['Total Minutes in Bed'] = df_sleep['Total Minutes in Bed'].sum()
                        feature_vector_sleep['Efficiency'] = df_sleep['Efficiency'].mean()
                        feature_vector_sleep['Wake After Sleep Onset (WASO)'] = df_sleep['Wake After Sleep Onset (WASO)'].sum()
                        feature_vector_sleep['Number of Awakenings'] = df_sleep['Number of Awakenings'].sum()
                        feature_vector_sleep['Average Awakening Length'] = df_sleep['Average Awakening Length'].mean()
                        feature_vector_sleep['Movement Index'] = df_sleep['Movement Index'].mean()
                        feature_vector_sleep['Fragmentation Index'] = df_sleep['Fragmentation Index'].mean()
                        feature_vector_sleep['Sleep Fragmentation Index'] = df_sleep['Sleep Fragmentation Index'].mean()

                    # Convert 'In Bed Time', 'Out Bed Time', 'Onset Time' columns to minutes past noon
                    time_columns = ['In Bed Time', 'Out Bed Time', 'Onset Time']
                    for col in time_columns:
                        orario = pd.to_datetime(feature_vector_sleep[col], format='%H:%M')
                        if orario.hour == 00:
                            feature_vector_sleep[col] = (12) * 60 + orario.minute
                        elif orario.hour <= 23 and orario.hour >= 12:
                            feature_vector_sleep[col] = (orario.hour - 12) * 60 + orario.minute
                        else:
                            feature_vector_sleep[col] = (orario.hour + 12) * 60 + orario.minute

                    # WORKING ON df_rr DATAFRAME
                    # Convert 'time' column to datetime format and extract the hour
                    df_rr['time'] = pd.to_datetime(df_rr['time'], format='%H:%M:%S').dt.hour
                    # Convert 'day' column values to string type
                    df_rr['day'] = df_rr['day'].astype(str)

                    # Calculate new features from RR.csv
                    rr_hourly_stats = df_rr.groupby(['day', 'time'])['ibi_s'].agg(['mean', 'std', kurtosis, skew, entropy])

                    actual_time = 9
                    for (day, time), stats in rr_hourly_stats.iterrows():
                        # we need to go up to 9 AM on day 2
                        if actual_time != 34:
                            while time != actual_time and time != actual_time - 24:
                                if actual_time >= 24:
                                    time_hole = actual_time - 24
                                else:
                                    time_hole = actual_time
                                feature_vector_sleep[f'Mean_{day}_{time_hole}'] = 0
                                feature_vector_sleep[f'DvSt_{day}_{time_hole}'] = 0
                                feature_vector_sleep[f'Kurtosis_{day}_{time_hole}'] = 0
                                feature_vector_sleep[f'Skew_{day}_{time_hole}'] = 0
                                feature_vector_sleep[f'Entropy_{day}_{time_hole}'] = 0
                                actual_time += 1
                            feature_vector_sleep[f'Mean_{day}_{time}'] = stats['mean']
                            feature_vector_sleep[f'DvSt_{day}_{time}'] = stats['std']
                            feature_vector_sleep[f'Kurtosis_{day}_{time}'] = stats['kurtosis']
                            feature_vector_sleep[f'Skew_{day}_{time}'] = stats['skew']
                            feature_vector_sleep[f'Entropy_{day}_{time}'] = stats['entropy']
                            actual_time += 1

                    # we need to go up to 9 AM on day 2, if not present, fill with 0
                    while actual_time != 34:
                        if actual_time >= 24:
                            time_hole = actual_time - 24
                        else:
                            time_hole = actual_time
                        feature_vector_sleep[f'Mean_{day}_{time_hole}'] = 0
                        feature_vector_sleep[f'DvSt_{day}_{time_hole}'] = 0
                        feature_vector_sleep[f'Kurtosis_{day}_{time_hole}'] = 0
                        feature_vector_sleep[f'Skew_{day}_{time_hole}'] = 0
                        feature_vector_sleep[f'Entropy_{day}_{time_hole}'] = 0
                        actual_time += 1

                    # WORKING ON df_actigraph DATAFRAME
                    # Convert 'time' column to datetime format and extract the hour
                    df_actigraph['time'] = pd.to_datetime(df_actigraph['time'], format='%H:%M:%S').dt.hour
                    # Convert 'day' column values to string type
                    df_actigraph['day'] = df_actigraph['day'].astype(str)

                    # Calculate new features from Actigraph.csv
                    hourly_steps = df_actigraph.groupby(['day', 'time'])['Steps'].sum()
                    hr_hourly_stats = df_actigraph.groupby(['day', 'time'])['HR'].agg(['mean', 'std'])
                    vm_hourly_stats = df_actigraph.groupby(['day', 'time'])['Vector Magnitude'].agg(['mean', 'std'])

                    actual_time = 9
                    for (day, time), hr_stats in hr_hourly_stats.iterrows():
                        vm_stats = vm_hourly_stats.loc[(day, time)]
                        if actual_time != 34:
                            while time != actual_time and time != actual_time - 24:
                                if actual_time >= 24:
                                    time_hole = actual_time - 24
                                else:
                                    time_hole = actual_time
                                feature_vector_sleep[f'Steps_{day}_{time_hole}'] = 0
                                feature_vector_sleep[f'Mean_HR_{day}_{time_hole}'] = 0
                                feature_vector_sleep[f'DvSt_HR_{day}_{time_hole}'] = 0
                                feature_vector_sleep[f'Mean_VM_{day}_{time_hole}'] = 0
                                feature_vector_sleep[f'DvSt_VM_{day}_{time_hole}'] = 0
                                actual_time += 1
                            feature_vector_sleep[f'Steps_{day}_{time}'] = hourly_steps.get((day, time), 0)
                            feature_vector_sleep[f'Mean_HR_{day}_{time}'] = hr_stats['mean']
                            feature_vector_sleep[f'DvSt_HR_{day}_{time}'] = hr_stats['std']
                            feature_vector_sleep[f'Mean_VM_{day}_{time}'] = vm_stats['mean']
                            feature_vector_sleep[f'DvSt_VM_{day}_{time}'] = vm_stats['std']
                            actual_time += 1

                    # we need to go up to 9 AM on day 2, if not present, fill with 0
                    while actual_time != 34:
                        if actual_time >= 24:
                            time_hole = actual_time - 24
                        else:
                            time_hole = actual_time
                        feature_vector_sleep[f'Steps_{day}_{time_hole}'] = 0
                        feature_vector_sleep[f'Mean_HR_{day}_{time_hole}'] = 0
                        feature_vector_sleep[f'DvSt_HR_{day}_{time_hole}'] = 0
                        feature_vector_sleep[f'Mean_VM_{day}_{time_hole}'] = 0
                        feature_vector_sleep[f'DvSt_VM_{day}_{time_hole}'] = 0
                        actual_time += 1


                    # WORK ON DATAFRAME df_questionnaire

                    stai_class = df_questionnaire['STAI2'].iloc[0]
                    
                    '''
                    # Assign "low" or "high" labels based on bisbas_class value
                    #if bisbas_class < 18.2:
                    #if bisbas_class < 14.6:
                    #if bisbas_class < 10.6:
                    #if bisbas_class < 9.5:
                    if bisbas_class < 9.5:
                        bisbas_label = "low"
                    else:
                        bisbas_label = "high"
                    '''

                    # Add user to feature vector
                    feature_vector_sleep['user'] = directory
                    # Add the new class to the feature vector
                    feature_vector_sleep['STAI2'] = stai_class
                    # Add the feature vector to the list
                    feature_vectors.append(feature_vector_sleep)
    
    return feature_vectors



def fill_holes(data):
    filled_data = data.copy()
    stats = ['Mean', 'DvSt', 'Kurtosis', 'Skew', 'Entropy', 'Steps', 'Mean_HR', 'DvSt_HR', 'Mean_VM', 'DvSt_VM']
    
    # For each row in the DataFrame
    for index, row in filled_data.iterrows():
        # Iterate over all days and hours in the file
        for day in ['1', '2']:
            if day == '1':
                hours = range(9, 24)  # Hours from 9 to 23 for day 1
            else:
                hours = range(0, 10)  # Hours from 0 to 9 for day 2

            for hour in hours:
                str_hour = str(hour)
                hour_prefix = f'{day}_{str_hour}'
                current_stats = [f'{stat}_{hour_prefix}' for stat in stats if f'{stat}_{hour_prefix}' in filled_data.columns]
                
                # Check if current hour is empty
                if all(filled_data.at[index, stat] == 0 for stat in current_stats):
                    print(f"Empty hour found: Day {day}, Hour {hour} ({row['user']})")

                    # Calculation of replacement hour
                    if hour == 9 and day == '1':
                        replacement_hour = '1_10'
                    elif hour == 9 and day == '2':
                        replacement_hour = '2_8'
                    else:
                        prev_hour = 23 if hour == 0 else hour - 1
                        next_hour = 0 if hour == 23 else hour + 1
                        prev_day = '1' if day == '1' or hour == 0 else '2'
                        next_day = '1' if day == '1' and hour < 23 else '2'
                        
                        prev_hour_prefix = f'{prev_day}_{prev_hour}'
                        next_hour_prefix = f'{next_day}_{next_hour}'
                        replacement_hour = None

                    # Value replacement
                    if replacement_hour:
                        replacement_stats = [f'{stat}_{replacement_hour}' for stat in stats if f'{stat}_{replacement_hour}' in filled_data.columns]
                        for stat, repl_stat in zip(current_stats, replacement_stats):
                            filled_data.at[index, stat] = row[repl_stat]
                    else:
                        prev_stats = [f'{stat}_{prev_hour_prefix}' for stat in stats if f'{stat}_{prev_hour_prefix}' in filled_data.columns]
                        next_stats = [f'{stat}_{next_hour_prefix}' for stat in stats if f'{stat}_{next_hour_prefix}' in filled_data.columns]
                        for stat, prev_stat, next_stat in zip(current_stats, prev_stats, next_stats):
                            if prev_stat in filled_data.columns and next_stat in filled_data.columns:
                                filled_data.at[index, stat] = (row[prev_stat] + row[next_stat]) / 2
    
    return filled_data



def extract_features(path_directory):
    # Creating dataset folder if it does not exist
    os.makedirs(os.getcwd() + "/Datasets", exist_ok=True)
    
    feature_vectors = get_feature_vectors(path_directory)

    # Create a DataFrame from feature vectors
    all_data = pd.DataFrame(feature_vectors)
    # Move the user column to the beginning of the dataframe
    all_data = all_data[['user'] + [col for col in all_data.columns if col != 'user']].reset_index(drop=True)
    # Fill temporal gaps
    filled_data = fill_holes(all_data)

    # Save feature vectors to a csv file
    output_file_path = os.path.join('Datasets', 'sleep_features.csv')
    filled_data.to_csv(output_file_path, index=False)

    print(f"Feature vectors saved to {output_file_path}")


if __name__=="__main__":
    # Directory path
    path_directory = "./DataPaper"
    extract_features(path_directory)
