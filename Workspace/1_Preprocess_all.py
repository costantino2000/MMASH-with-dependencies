# This script calls the other preprocessing scripts to create the preprocessed data
# The individual scripts will save their outputs in the Logs folder

import preprocess_actigraph as pra
import preprocess_rr as prr
import utilities.library as lib

if __name__=="__main__":
    path, users = lib.get_path_and_users("RR")
    print("Preprocessing Actigraph data...\n")
    pra.preprocessing(path, users, 100)
    print("\n\nPreprocessing RR data...")
    prr.preprocessing(path, users)
