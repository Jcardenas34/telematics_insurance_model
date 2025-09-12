import joblib
import pandas as pd

from telematics_insurance_model.helpers.feature_selection import traditional_features, telematics_features, all_feature_cols
from telematics_insurance_model.helpers.logger import initialize_evaluation_logger



def main():
        
    # Load simulated telematics data
    data_path = "data/trip_records/trip_analyses.csv"

    evaluation_df = pd.read_csv(data_path)
    # print(evaluation_df.columns)



    # Determining which features to use
    # feature_cols = all_feature_cols
    # feature_cols = traditional_features
    feature_cols = telematics_features

    model_name = "traditional+telematics"  # options: "traditional", "telematics", "traditional+telematics"

    if feature_cols == traditional_features:
        print("Using traditional features only")
        model_name = "traditional"
    elif feature_cols == telematics_features:
        print("Using telematics features only")
        model_name = "telematics"
    else:
        print("Using traditional + telematics features")




    # Initialize a logger to keep track of training and evaluation status
    logger = initialize_evaluation_logger(model_name=model_name)

    logger.info(f"Starting evaluation of Logistic Regression model with dataset: {data_path}")
    logger.info(f"Using features: {feature_cols}")



    # Extracting feature matrix
    X = evaluation_df[feature_cols]


    filename = f'log_reg_{model_name}.pkl'
    pipeline = joblib.load("models/"+filename)

    logger.info("Pipeline loaded successfully.")
    print("Pipeline loaded successfully.")

    logger.info(f"Loaded pipeline from models/{filename}")
    print(f"Loaded pipeline from models/{filename}")


    # Evaluate performance on test set
    logger.info("Evaluating performance on test set...")

    # ----------------------------
    # Step 5: Attach risk scores back to dataset
    # ----------------------------
    evaluation_df["risk_factor"] = pipeline.predict_proba(X)[:, 1]

    # Example: premium calculation
    base_premium = 300
    alpha = 1000
    evaluation_df["premium"] = base_premium + alpha * evaluation_df["risk_factor"]

    # Save the dataset with risk scores and premiums
    evaluation_df.to_csv("data/trip_records/generated_dataset_with_risk_scores.csv")


    logger.info("Dataset with risk scores and premiums saved to data/trip_records/generated_dataset_with_risk_scores.csv")
    print("Dataset with risk scores and premiums saved to data/trip_records/generated_dataset_with_risk_scores.csv")
    logger.info("Model evaluation completed.")
    print("Model evaluation completed.") 


if __name__ == "__main__":
    main()