import os
import pandas as pd

from telematics_insurance_model.helpers.feature_selection   import drop_arr
from telematics_insurance_model.utils.append_telematics     import append_telematics
from telematics_insurance_model.helpers.feature_engineering import add_age_and_years_driving



def main():

    n_samples = None
    n_samples = 1000

    print("Preprocessing a datafile with n_samples =", n_samples, "...")

    os.makedirs('data/preprocessed_data', exist_ok=True)

    # Load in original dataset
    df = pd.read_csv("data/real_dataset/Motor_vehicle_insurance_data.csv", sep=";")

    # Gather a random subsample if in debug mode
    if n_samples:
        df = df.sample(n_samples)


    # Add age and years driving features
    df = add_age_and_years_driving(df)

    # Keep only the training features, by dropping unnecessary features
    df.drop(columns=drop_arr, inplace=True)


    # Transform yearly data into monthly data with telematics features
    df = append_telematics(df)


    # Save the dataset
    data_path = "data/preprocessed_data/"
    if n_samples:
        df.to_csv(f"{data_path}/processed_dataset_{n_samples}.csv", sep=";", index=False)
        print(f"Processed data saved to {data_path}/processed_dataset_{n_samples}.csv")
    else:
        # Save the processed dataframe
        df.to_csv("{data_path}/processed_dataset.csv", sep=";", index=False)
        print("Processed data saved to {data_path}/processed_dataset.csv")




if __name__ == "__main__":
    """Module for data preprocessing in telematics insurance model."""
    
    main()