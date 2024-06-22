# Script to be executed after all train sets with the STAI2 values have been created, it allows
# to change the metric with those of the others questionnaires to test them separately

import function_code.open_data as open_data
import utilities.library as lib
import pandas as pd
import os


def save_to_csv(datasets_path, column, dataset, df_dataset):
    # Each dataset variant gets its own folder
    os.makedirs(datasets_path + column, exist_ok=True)
    df_dataset.to_csv(datasets_path + column + "/" + dataset)
    

def create_variants(questionnaire_path, users):
    # Setting the paths and datasets to be changed
    datasets_path = os.getcwd() + "/Datasets/"
    datasets_to_change = ["train_set_v5_clean.csv", "train_set_v6_clean.csv"]
    panas_pos_columns = ["panas_pos_10", "panas_pos_14", "panas_pos_18", "panas_pos_22", "panas_pos_9+1"]
    panas_neg_columns = ["panas_neg_10", "panas_neg_14", "panas_neg_18", "panas_neg_22", "panas_neg_9+1"]
    
    # Saving questionnaire data to dataframe
    df_questionnaire = open_data.create_dataset(questionnaire_path, users, 'questionnaire').reset_index()
    
    # For each dataset, create corresponding variants where the STAI2 column
    # is replaced by another questionnaire column
    for dataset in datasets_to_change:
        df_dataset = pd.read_csv(datasets_path + dataset).drop(columns=["STAI2"])
        for column in df_questionnaire.columns:
            
            if column == "panas_pos_10":
                df_panas_pos = df_questionnaire[panas_pos_columns]
                # Calculate the mean of panas values for each row
                df_dataset["panas_pos_mean"] = round(df_panas_pos.mean(axis=1), 0)
                save_to_csv(datasets_path, "panas_pos_mean", dataset, df_dataset)
                df_dataset = df_dataset.drop(columns=["panas_pos_mean"])
                
            if column == "panas_neg_10":
                df_panas_neg = df_questionnaire[panas_neg_columns]
                # Calculate the mean of panas values for each row
                df_dataset["panas_neg_mean"] = round(df_panas_neg.mean(axis=1), 0)
                save_to_csv(datasets_path, "panas_neg_mean", dataset, df_dataset)
                df_dataset = df_dataset.drop(columns=["panas_neg_mean"])
            
            if column != "user" and not column.startswith("panas"):
                # Yes, we also create a folder for STAI2 for when we test everything together
                df_dataset[column] = df_questionnaire[column]
                save_to_csv(datasets_path, column, dataset, df_dataset)
                df_dataset = df_dataset.drop(columns=[column])
                
    print("Done!")


if __name__=="__main__":
    questionnaire_path, users = lib.get_path_and_users("questionnaire")
    create_variants(questionnaire_path, users)
    