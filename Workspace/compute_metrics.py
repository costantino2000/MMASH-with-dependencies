# This script takes an array of couples as input (true value, predicted value),
# computes the metrics and returns them with the output to be printed

import numpy as np

# Thresholds indicating different ranges of the questionnaire results (e.g., 30, 50 means up to 30 class 1, up to 50 class 2, and above 3)
tresholds = {
    "MEQ": [40, 60],
    "STAI1": [30, 50],
    "STAI2": [30, 50]
}

# Minimum and maximum values of the questionnaires (to truncate the values later)
questionnaire_ranges = {
    # For BISBAS we had to rely on typically used ones, except for "reward" which did not follow the norm
    "BISBAS_bis": [7, 28],
    "BISBAS_drive": [4, 16],
    "BISBAS_fun": [4, 16],
    "BISBAS_reward": [7, 28],
    "Daily_stress": [0, 406],
    "MEQ": [16, 86],
    "Pittsburgh": [0, 21],
    "panas_pos_mean": [5, 50],
    "panas_neg_mean": [5, 50],
    "STAI1": [20, 80],
    "STAI2": [20, 80]
}

def calculate_metrics(results, questionnaire, min_quest_value, max_quest_value):
    # Iterate through the results updating max, min errors, also calculating the mean
    max_error = 0
    min_error = 1000
    mean_error = 0

    correct_labels = 0
    wrong_labels = 0
    very_wrong_labels = 0
    
    # The score range of the test users' values
    data_range = max_quest_value - min_quest_value

    deviations = []
    for pair in results:        # The pairs are true value, predicted value
        true_value = pair[0]
        predicted_value = pair[1]
        
        # First, make the predicted value fall within the range of the questionnaire
        min_value = questionnaire_ranges[questionnaire][0]
        max_value = questionnaire_ranges[questionnaire][1]
        if predicted_value < min_value:
            predicted_value = min_value
        if predicted_value > max_value:
            predicted_value = max_value
        
        deviation = abs(true_value - predicted_value)
        if deviation < min_error: min_error = deviation
        if deviation > max_error: max_error = deviation
        mean_error += deviation
        deviations.append(deviation)
        
        # If the questionnaire can be split into three ranges, also count the number of correctly or incorrectly labeled instances
        if questionnaire in tresholds.keys():
            treshold_list = tresholds[questionnaire]
            # Check if the predicted label belongs to the same range as the correct one
            true_class = 1 if true_value < treshold_list[0] else (2 if true_value < treshold_list[1] else 3)
            predicted_class = 1 if predicted_value < treshold_list[0] else (2 if predicted_value < treshold_list[1] else 3)
            class_difference = abs(predicted_class - true_class)

            if class_difference == 0:
                correct_labels += 1
            elif class_difference == 1:
                wrong_labels += 1
            elif class_difference == 2:
                very_wrong_labels += 1

    mean_error /= len(results)
    
    # The percentage of the mean error relative to the users' value range
    error_ratio = (mean_error / data_range) * 100

    std_dev = np.std(deviations)
    
    results = {
        "mean_error": round(mean_error, 2),
        "max_error": round(max_error, 2),
        "min_error": round(min_error, 2),
        "std_dev": round(std_dev, 2),
        "error_ratio": round(error_ratio, 2),
        # If the label count is available, it will be set later
        "correct_labels_total": "not_available",
        "wrong_labels_total": "not_available",
        "very_wrong_labels_total": "not_available"
    }

    # Create a string to return to the test function for printing and saving
    results_text = ("Mean error: " + str(results["mean_error"])
     + "\nMax error: " + str(results["max_error"])
     + "\nMin error: " + str(results["min_error"])
     + "\nStandard deviation: " + str(results["std_dev"]))
    
    if questionnaire in tresholds.keys():
        results["correct_labels_total"] = str(correct_labels) + "/" + str(len(results))
        results["wrong_labels_total"] = str(wrong_labels) + "/" + str(len(results))
        results["very_wrong_labels_total"] = str(very_wrong_labels) + "/" + str(len(results))
        results_text += ("\nCorrectly labeled instances: " + results["correct_labels_total"]
         + "\nIncorrectly labeled instances: " + results["wrong_labels_total"]
         + "\nVery incorrectly labeled instances: " + results["very_wrong_labels_total"])
    
    return results, results_text
