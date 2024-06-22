# Script that creates a Poincare plot with IBI values

import os
import pandas as pd
import numpy as np
import function_code.open_data as open_data
import function_code.HRV_analysis as HRV_analysis
import warnings
warnings.filterwarnings("ignore")


if __name__=="__main__":
    # Create a list of users
    path = os.getcwd() + "/DataPaper/"
    users = os.listdir(path)

    # Retrieve heart rate data
    df_rr = open_data.create_dataset(path, users, 'RR').reset_index()

    # Time conversion: 0 refers to noon, while positive and negative values refer to pre and post-midnight data
    df_rr['timestamp'] = [float(x.split(':')[0])*60*60 + float(x.split(':')[1])*60 + float(x.split(':')[2]) if y==1 else 
                            float(x.split(':')[0])*60*60 + float(x.split(':')[1])*60 + float(x.split(':')[2]) + 24*60*60
                            for x,y in zip(df_rr['time'],df_rr['day'])]

    # Filter out ectopic beats
    df_rr['ibi_s'] = [x if x<2 else np.nan for x in df_rr['ibi_s']]
    df_rr['ibi_s'] = [x if x>0.3 else np.nan for x in df_rr['ibi_s']]

    df_user = df_rr[df_rr['user']=="user_1"].dropna()

    # Select a 5-minute time window for HRV analysis
    df_user["window"] = df_user.timestamp.diff().dropna().cumsum().pipe(lambda x: pd.to_timedelta(x, "s")).dt.floor("5min")
    print(df_user)
    print(df_user.window)
    df_window = df_user[df_user.window.astype(str) == '0 days 20:00:00.000000000']

    HRV_analysis.plot_HRV(df_window)
