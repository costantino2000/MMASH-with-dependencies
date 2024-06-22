# This script will create the train sets used for testing

import extract_sleep_features as esf
import create_datasets as cd
import utilities.library as lib
import create_dataset_variants as cdv


if __name__=="__main__":
    path, users = lib.get_path_and_users("Actigraph", "Actigraph-processed", "RR", "RR-processed")

    # Note: the sleep features are also extracted from unprocessed rr and actigraph data
    print("\nExtracting sleep features...")
    esf.extract_features(path)

    print("\nCreating first 4 datasets with unprocessed data...")
    cd.create_dataset(path, users, False, [1, 2, 3, 4])

    print("\nCreating datasets v4, v5 and v6 with processed data...")
    cd.create_dataset(path, users, True, [4, 5, 6])
    
    print("\nCreating datasets variants with every questionnaire...")
    cdv.create_variants(path, users)
    