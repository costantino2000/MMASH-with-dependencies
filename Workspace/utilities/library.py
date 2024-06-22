import os
import sys
import shutil


# New version that only checks if the files exist
def file_check_simple(path, users, dataset_name):
    for user in users:
        user_folder = os.path.join(path, user)
        dataset_file_path = os.path.join(user_folder, dataset_name + '.csv')

        if not os.path.isfile(dataset_file_path):
            print("Error! The", dataset_name, "file for", user, "is missing.")
            sys.exit()


# It's not a real logger because it doesn't save to a file; the logic still lies in the individual scripts
def logger(string, log, print_string=True):
    if print_string:
        print(string)
    log.append(string + "\n")


# Checks if all dataset names passed exist
def get_path_and_users(*dataset_names):
    path = os.getcwd() + '/DataPaper/'
    users = os.listdir(path)
    
    if '.DS_Store' in users:
        users.remove('.DS_Store')

    print("Checking files...")
    for dataset in dataset_names:
        file_check_simple(path, users, dataset)

    return path, users
