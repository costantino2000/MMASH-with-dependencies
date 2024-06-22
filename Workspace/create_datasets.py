# This script extracts the features mentioned in the paper and creates the train sets

import os
import numpy as np
import pandas as pd
import functools
import function_code.open_data as open_data
import function_code.HRV_analysis as HRV_analysis
import function_code.circadian as circadian
import utilities.library as lib
import warnings
warnings.filterwarnings("ignore")


def compute_rmssd(group):
    # Calculate successive differences
    diff = group['ibi_s'].diff().dropna()   # Removes NaN elements
    # Square each difference
    diff_squared = diff ** 2
    # Calculate the mean of squared differences
    mean_squared_diff = diff_squared.mean()
    # Calculate the square root of the mean obtained
    rmssd = mean_squared_diff ** 0.5
    return rmssd


def compute_ratio(group):
    # Calculate successive differences
    diff = group['ibi_s'].diff().dropna()   # Removes NaN elements
    # Find differences greater than 50 ms
    diff_greater_than_50 = diff[abs(diff) > 0.05]
    # Calculate the total number of IBI
    total_IBIs = len(group)
    # Calculate the number of successive IBI pairs that differ by more than 50 ms
    num_pairs_diff_greater_than_50 = len(diff_greater_than_50)
    # Calculate the required ratio
    ratio = num_pairs_diff_greater_than_50 / total_IBIs
    return ratio


def compute_freq(group):
    nn_intervals = list(1000 * group['ibi_s'].dropna().values)
    freq, psd = HRV_analysis._get_freq_psd_from_nn_intervals(nn_intervals=nn_intervals, sampling_frequency = 7)

    vlf_indexes = np.logical_and(freq >= 0.003, freq < 0.04)
    lf_indexes = np.logical_and(freq >= 0.04, freq < 0.15)
    hf_indexes = np.logical_and(freq >= 0.15, freq < 0.40)

    vlf_power = np.trapz(psd[vlf_indexes], freq[vlf_indexes])
    lf_power = np.trapz(psd[lf_indexes], freq[lf_indexes])
    hf_power = np.trapz(psd[hf_indexes], freq[hf_indexes])
    total_power = np.trapz(psd, freq)

    return {"vlf": vlf_power, "lf": lf_power, "hf": hf_power, "total_power": total_power}


def compute_sd(group):
    nn_intervals = list(1000 * group['ibi_s'].dropna().values)
    diff_nn_intervals = np.diff(nn_intervals)
    sd1 = np.sqrt(np.std(diff_nn_intervals, ddof=1) ** 2 * 0.5)
    sd2 = np.sqrt(2 * np.std(nn_intervals, ddof=1) ** 2 - 0.5 * np.std(diff_nn_intervals, ddof=1) ** 2)
    return {"SD1": sd1, "SD2": sd2, "SD1/SD2": (sd1/sd2)*10}


def compute_anomalies_percentage(group):
    n_anomalies = len(group[group["Anomaly"] == True].index)
    cond_inclinometer_1 = group['Inclinometer Sitting'] == 1.0
    cond_inclinometer_2 = group['Inclinometer Lying'] == 1.0
    rows_while_sitting_or_lying = len(group[cond_inclinometer_1 | cond_inclinometer_2].index)
    anomalies_percentage = round((n_anomalies / rows_while_sitting_or_lying) * 100, 2)
    return anomalies_percentage


def compute_mesor(group):
    # Calculate MESOR using the formula MESOR = offset + (amplitude * cos(phase))
    return group['offset'] + (group['amp'] + np.cos(group['phase']))

def time_to_seconds(time, day):
    seconds = float(time.split(':')[0])*60*60 + float(time.split(':')[1])*60 + float(time.split(':')[2])
    if (day != 1):
        seconds += 24*60*60
    return seconds

def compute_sinusoid_data(group):
    # Transform Time format in seconds. 0 refers to 12 AM, while positive and negative values refer to pre and post midnight, respectively.
    group['timestamp'] = [time_to_seconds(time, day) for time, day in zip(group['time'], group['day'])]

    # Compute Heart Rate values from ibi
    group['hr'] = [60/ibi for ibi in group['ibi_s']]
    group = group.dropna()
    
    # Fit single component cosinor curves
    res = circadian.fit_sin(group['timestamp'], group['hr'].rolling(60, min_periods=1).mean())
    # res2 = circadian.fit_multi(group['timestamp'], group['hr'].rolling(60,min_periods=1).mean(), plot=True)
    
    del res["r2"]
    del res["tt"]
    del res["ff"]
    
    return res


# Dataset versions is a list that contains the versions of the dataset to create
def create_dataset(path, users, use_processed_data, dataset_versions):
    os.makedirs(os.getcwd() + "/Datasets", exist_ok=True)

    count_anomalies = False
    if 4 in dataset_versions or 5 in dataset_versions or 6 in dataset_versions:
        count_anomalies = True
    
    if count_anomalies:     # Set first to crash immediately if the script is not executed
        print("Loading actigraph data...")
        df_actigraph = open_data.create_dataset(path, users, 'Actigraph-processed').reset_index()
        print("Counting anomalies...")
        df_anomalies = df_actigraph.groupby("user").apply(compute_anomalies_percentage).rename('Anomalies')
        # print(df_anomalies)
    
    # It is better to have cleaned the data beforehand

    print("Loading RR data...")
    
    rr_dataset = 'RR-processed' if use_processed_data else 'RR'
    df_rr = open_data.create_dataset(path, users, rr_dataset).reset_index()
    
    df_rr = df_rr[['user', 'ibi_s', 'time', 'day']]
    
    # Filter ectopic beats (those with a distance < 0.3 / > 2 seconds from the previous one)
    df_rr['ibi_s'] = [x if x<2 else np.nan for x in df_rr['ibi_s']]
    df_rr['ibi_s'] = [x if x>0.3 else np.nan for x in df_rr['ibi_s']]
    
    
    print("Calculating HR_mean...")
    dr_hr = df_rr.copy()
    dr_hr['ibi_s'] = 60 / dr_hr["ibi_s"] * 10   # The *10 is to have the data as in the paper
    df_hr_mean = dr_hr.groupby("user").mean().rename(columns={"ibi_s": "HR_mean"})
    # print(df_hr_mean)
    
    
    print("Calculating RMSSD...")
    df_rmssd = df_rr.groupby('user').apply(compute_rmssd).rename('RMSSD') * 1000
    # print(df_rmssd)
    

    print("Calculating SDNN...")
    df_std = df_rr.groupby("user").std().rename(columns={"ibi_s": "SDNN"}) * 1000
    # print(df_std)
    

    print("Calculating PNN50...")
    df_pnn50 = df_rr.groupby('user').apply(compute_ratio).rename('PNN50') * 100
    # print(df_pnn50)
    

    print("Calculating frequencies...")
    freq_data = df_rr.groupby("user").apply(compute_freq)
    df_freq = pd.DataFrame(freq_data.tolist(), index=freq_data.index)
    # print(df_freq)
    

    print("Calculating SD1 and SD2...")
    SD_data = df_rr.groupby('user').apply(compute_sd)
    df_SD = pd.DataFrame(SD_data.tolist(), index=SD_data.index)
    # print(df_SD)


    print("Calculating sinusoid data...")
    df_sinusoid = df_rr.copy()
    sinusoid_data = df_sinusoid.groupby('user').apply(compute_sinusoid_data)
    df_sinusoid = pd.DataFrame(sinusoid_data.tolist(), index=sinusoid_data.index)
    # print(df_sinusoid)
    df_sinusoid['MESOR'] = df_sinusoid.apply(compute_mesor, axis=1).rename('MESOR')
    del df_sinusoid['phase']
    del df_sinusoid['offset']
    # print(df_sinusoid)
    
    
    if 6 in dataset_versions:   # only train_set_v6 has the sleep features
        print("Retrieving sleep features...")
        df_sleep = pd.read_csv(os.getcwd() + "/Datasets/sleep_features.csv").drop(columns=["STAI2"])
        # print(df_sleep)


    print("Retrieving STAI2 values...")
    df_stai2 = open_data.create_dataset(path, users, 'questionnaire').reset_index()[['user',"STAI2"]]
    # print(df_stai2)


    print("Merging dataframes and saving to file...")
    dfs1 = [df_hr_mean, df_rmssd, df_std, df_pnn50, df_stai2]
    dfs2 = [df_hr_mean, df_rmssd, df_std, df_pnn50, df_freq, df_SD, df_stai2]
    dfs3 = [df_hr_mean, df_rmssd, df_std, df_pnn50, df_freq, df_stai2]
    datasets = [dfs1, dfs2, dfs3]
    if count_anomalies:
        dfs4 = [df_hr_mean, df_rmssd, df_std, df_pnn50, df_freq, df_SD, df_anomalies, df_sinusoid, df_stai2]
        datasets.append(dfs4)
        dfs5 = dfs4     # Set 5 will remove users 4 and 7
        datasets.append(dfs5)
        if 6 in dataset_versions:
            dfs6 = [df_hr_mean, df_rmssd, df_std, df_pnn50, df_freq, df_SD, df_anomalies, df_sinusoid, df_stai2, df_sleep]
            datasets.append(dfs6)

    for version in dataset_versions:        # Take each dataset to create from the list passed before
        df_merged = functools.reduce(lambda left, right: pd.merge(left, right, on=['user']), datasets[version - 1])
        del df_merged["day_x"]
        del df_merged["day_y"]
        # print(df_merged)
        df_merged = df_merged.round(2).set_index("user")
        if use_processed_data:
            print("Creating train_set_v{}_clean.csv".format(version))
            if version == 5 or version == 6:
                df_merged2 = df_merged.drop("user_4").dropna()
                df_merged2.to_csv(os.getcwd() + "/Datasets/train_set_v{}_clean.csv".format(version))
            else:
                df_merged.to_csv(os.getcwd() + "/Datasets/train_set_v{}_clean.csv".format(version))
        else:
            print("Creating train_set_v{}.csv".format(version))
            df_merged.to_csv(os.getcwd() + "/Datasets/train_set_v{}.csv".format(version))

    print("Done!")



if __name__=="__main__":
    path, users = lib.get_path_and_users("RR")  # We only check RR for the case where processed data is not used
    create_dataset(path, users, True, [4])
