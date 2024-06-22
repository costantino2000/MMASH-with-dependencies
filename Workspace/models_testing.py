# This script does feature selection and trains the models with the received data to give back predictions

from sklearn.feature_selection import SelectFromModel
from sklearn.feature_selection import f_regression, r_regression, mutual_info_regression


def selectFeatures(model, X):
    selector = SelectFromModel(model, prefit=True)
    feature_idx = selector.get_support()
    feature_names = X.columns[feature_idx]
    return feature_names


# Automatic feature selection
def doFeatSelection(model, X, Y):
    model.fit(X, Y)
    features = selectFeatures(model, X)
    return features


# Feature selection based on threshold indicating the importance of each feature
def featSelectionAdvanced(X, Y, threshold):  # To experiment, change the threshold and function in scores
    # scores = mutual_info_regression(X, Y, random_state=42)     # quite slow
    # scores = f_regression(X, Y)[0] # For f_regression we use f values
    scores = r_regression(X, Y)
    columns = list(X.columns.values)
    i = 0
    res = []
    while i < len(columns):
        if(scores[i] > threshold): res.append(columns[i])
        i = i + 1
    # Uncomment to see how many features are selected for each user (beware of terminal spam)
    # print("Num. features selected:", len(res))
    return res
    

def fit_and_predict(model, support_feat_select, train, test):
    features_num = len(train["X"].columns)

    support_feat_select = True  # The if condition must always be true for advanced feature selection
    if support_feat_select:
        # features = doFeatSelection(model, train["X"], train["Y"])     # Automatic feature selection
        features = featSelectionAdvanced(train["X"], train["Y"], 0.1)   # Change the threshold to experiment (check the values first)
        train["X"] = train["X"][features]
        test["X"] = test["X"][features]
        features_num = len(features)
    
    # Train the model on the training data
    model.fit(train["X"], train["Y"])
    
    # Make a prediction on the test data
    y_pred = model.predict(test["X"])
    
    # Return a tuple with the true value and the prediction (which is a numpy vector and must be unpacked), plus the number of selected features
    return (test["Y"], y_pred[0]), features_num
