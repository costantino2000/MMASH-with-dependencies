# This script runs various tests on a file specified in the program

# Since we have n users we run n tests on the selected model, using one user as test every time
# Every model gives back a couple (true value, predicted value) to be appended to the results variable
# To add a model add it to the models dict

from sklearn.linear_model import *
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB

import os
import pandas as pd
import compute_metrics
import models_testing as models_testing
import warnings
warnings.filterwarnings('ignore')   # otherwise lasso spams warnings because it doesn't converge


# Format: (name for print, sklearn model, whether it supports feature selection)
models = {
    0: ("All models", None, None),
    1: ("KNN", KNeighborsClassifier(n_neighbors=5), False),
    2: ("Random Forest", RandomForestClassifier(random_state=42), True),    # random_state to always get the same results
    3: ("Naive Bayes", GaussianNB(), False),
    4: ("Decision Tree", DecisionTreeClassifier(random_state=42), True),    # also here to remove randomness
    5: ("Support Vector Machine linear", SVC(kernel='linear'), True),
    6: ("Support Vector Machine rbf", SVC(kernel='rbf'), False),
    7: ("Support Vector Machine poly", SVC(kernel='poly'), False),
    8: ("Linear Regression Base", LinearRegression(), True),
    9: ("Linear Regression Ridge", Ridge(), True),
    10: ("Linear Regression Lasso", Lasso(), True),
}

# These are used to name the rows of the results dataframes
models_names = {
    0: "All",
    1: "KNN",
    2: "RandomForest",
    3: "NaiveBayes",
    4: "DecisionTree",
    5: "SvmLinear",
    6: "SvmRbf",
    7: "SvmPoly",
    8: "LinearRegression",
    9: "Ridge",
    10: "Lasso"
}


def chooseModel():
    print("Select the model to use:\n(numbers only, to change dataset and questionnaire go to the code)")
    for possible_choice in models.items():
        print(str(possible_choice[0]) + ")", possible_choice[1][0])
    print("Entering an invalid value closes the program")
    choice = int(input())
    if choice not in models.keys():
        print("Wrong choice")
        exit(0)
    return choice


def runTest(data, user_choice, X, y):
    # Loop for running the tests
    i = 0
    predictions = []
    faulty_iterations = []  # List containing the loops where no features were obtained with feature selection
    
    while i < len(data):    # Run the test on user i
        # Split between training and test set
        train = {
            "X": X.loc[~X.index.isin([i])],
            "Y": y.loc[~y.index.isin([i])]
        }
        test = {
            "X": pd.DataFrame(X.loc[i]).transpose(),
            "Y": y.loc[i]
        }
        # Execute the model selected by the user
        model = models[user_choice][1]
        do_feat_selection = models[user_choice][2]
        # If no features are selected because the threshold is too high
        # (in case of advanced feature selection) the user is skipped
        try:
            prediction, num_features = models_testing.fit_and_predict(model, do_feat_selection, train, test)
            global NUM_OF_FEATURES
            if NUM_OF_FEATURES == 0:
                NUM_OF_FEATURES = num_features
            else:
                NUM_OF_FEATURES = (NUM_OF_FEATURES + num_features) / 2
            predictions.append(prediction)
        except ValueError:      # beware, the same exception occurs if the feature vector is not unidimensional (e.g. f_regression gives two vectors, not one)
            faulty_iterations.append(i)
        i += 1

    if len(faulty_iterations) > 0:
        print(f"No features selected in iterations {faulty_iterations}, threshold too high?")
    # If feature selection never found features to train the model, return an empty dataframe
    if len(predictions) == 0:
        return pd.DataFrame()
        
    # After the execution, calculate the metrics and print them to the terminal
    results, results_text = compute_metrics.calculate_metrics(predictions, QUESTIONNAIRE, y.min(), y.max())
    print("\n" + results_text + "\n")
    
    # This part is only used when testing all models, to concatenate it to the dataframe that will be saved to file
    df_results = pd.DataFrame(results, index=[0])
    df_results["MODEL"] = models_names[user_choice]
    df_results = df_results.set_index("MODEL", drop=True)
    return df_results


# The main part of the code, separated from main to automate the test on all questionnaires
def main_loop(user_choice, datasets_path):
    # Read the dataset corresponding to the set questionnaire
    dataset_path = os.path.join(datasets_path, QUESTIONNAIRE, DATASET_NAME + ".csv")
    data = pd.read_csv(dataset_path).dropna()
    
    # Extract dependent and independent variables
    X = data[data.columns.difference(['user', QUESTIONNAIRE])]
    y = data[QUESTIONNAIRE]     # The value to predict is the questionnaire score
    
    # If you choose to test only one model, print the results (inside runTest) and end there
    if user_choice != 0:
        print("\nModel:", models[user_choice][0])
        runTest(data, user_choice, X, y)
        exit(0)
    
    # If all models are tested, the results will be saved in csv and excel files within the respective folders
    results_columns = ["MODEL", "mean_error", "max_error", "min_error", "std_dev", "correct_labels_total", "wrong_labels_total", "very_wrong_labels_total"]
    df_results = pd.DataFrame(columns=results_columns)    # Initialize an empty dataset to save the results for each iteration
    df_results = df_results.set_index("MODEL", drop=True)   # Once the columns are set, set the model name used as the index
    
    # Each model is tested and its results appended as a row to the results dataframe
    for model in models.keys():
        print("\nModel:", models[model][0])
        df_partial = runTest(data, model, X, y)
        df_results = pd.concat([df_results, df_partial], axis=0, join='outer', ignore_index=False, keys=None)

    # If the questionnaire cannot be split into three classes, the following columns do not matter:
    if df_results["correct_labels_total"].any() == "not_available":
        df_results = df_results.drop(columns=["correct_labels_total", "wrong_labels_total", "very_wrong_labels_total"])
        
    os.makedirs("Results/" + DATASET_NAME, exist_ok=True)
    results_file = os.path.join(os.getcwd(), "Results", DATASET_NAME, QUESTIONNAIRE)
    with open(results_file + ".csv", "w") as f:
        df_results.to_csv(f)
    with open(results_file + ".xlsx", "wb") as f:
        df_results.to_excel(f)
    
    print("The results have been saved to file\n")
    

def main():
    do_all_questionnaires = True        # Set to true to test all questionnaires (only works if you choose to test all models)
    
    datasets_path = os.path.join(os.getcwd(), "Datasets")
    # All the names of the questionnaires available in the datasets folder
    questionnaires = [entry for entry in os.listdir(datasets_path) if os.path.isdir(os.path.join(datasets_path, entry))]
    #questionnaires = ["BISBAS_bis", "BISBAS_drive", "BISBAS_fun", "BISBAS_reward", "Daily_stress", "MEQ", "Pittsburgh", "panas_pos_mean", "panas_neg_mean", "STAI1", "STAI2"]
    
    # Choose the model to use
    user_choice = chooseModel()
    if user_choice == 0:
        del models[0]  # The first is not a model, it is the choice to test them all, it is needed for the loop
        
    print("\nDataset:", DATASET_NAME)
    
    if do_all_questionnaires and user_choice == 0:
        for questionnaire in questionnaires:
            print("\n\nQuestionnaire:", questionnaire + "\n")
            global QUESTIONNAIRE
            QUESTIONNAIRE = questionnaire
            main_loop(user_choice, datasets_path)
    else:
        print("\n\nQuestionnaire:", QUESTIONNAIRE + "\n")
        main_loop(user_choice, datasets_path)
    

# Define global variables
if __name__ == "__main__":
    # Section of variables to set to change the tests
    DATASET_NAME = "train_set_v6_clean" # The dataset name without extension, used throughout the code
    QUESTIONNAIRE = "STAI2"             # If the option below is False, set the questionnaire here
    NUM_OF_FEATURES = 0                 # Used to average the number of features depending on the threshold in models_testing
    main()
    print("Average number of features selected during iterations:", NUM_OF_FEATURES)
