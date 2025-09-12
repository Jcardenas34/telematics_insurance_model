import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import logging

from telematics_insurance_model.helpers.feature_selection import traditional_features, telematics_features, all_feature_cols
from telematics_insurance_model.helpers.logger import initialize_training_logger




def main():
        
    data_path = "data/preprocessed_data/processed_dataset_10000.csv"

    # Load preprocessed data
    preprocessed_df = pd.read_csv(data_path, sep=";")


    # Target variable: monthly claims (binary)
    y = preprocessed_df["Claim_this_month"]

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
    logger = initialize_training_logger(model_name=model_name)

    logger.info(f"Starting training for Logistic Regression model with dataset: {data_path}")
    logger.info(f"Using features: {feature_cols}")



    # Extracting feature matrix
    X = preprocessed_df[feature_cols]

    # Split the training and testing data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)


    # Fit the traditional logistic regression alg. 
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("logreg", LogisticRegression(max_iter=1000, class_weight="balanced"))
    ])

    pipeline.fit(X_train, y_train)
    y_pred_proba = pipeline.predict_proba(X_test)[:, 1]


    # Ensure models directory exists
    os.makedirs('models', exist_ok=True)

    # Save the model
    filename = f'log_reg_{model_name}.pkl'
    joblib.dump(pipeline, "models/"+filename)

    print(f"Pipeline saved to models/{filename}")


    # Evaluate performance on test set
    logger.info("Logistic Regression model trained and saved.")
    logger.info("Evaluating performance on test set...")

    y_pred_proba = pipeline.predict_proba(X_test)[:, 1]  # risk score = probability of claim
    auc = roc_auc_score(y_test, y_pred_proba)
    print("ROC-AUC:", auc)

    logger.info(f"ROC-AUC: {auc:.4f}")
    print(classification_report(y_test, (y_pred_proba > 0.5).astype(int)))

    logger.info("Classification report:\n" + classification_report(y_test, (y_pred_proba > 0.5).astype(int)))


    # ----------------------------
    # Step 5: Attach risk scores back to dataset
    # ----------------------------
    preprocessed_df["risk_factor"] = pipeline.predict_proba(X)[:, 1]

    # Example: premium calculation
    base_premium = 300
    alpha = 1000
    preprocessed_df["premium"] = base_premium + alpha * preprocessed_df["risk_factor"]

    # Save the dataset with risk scores and premiums
    preprocessed_df.to_csv("data/preprocessed_data/processed_dataset_with_risk_scores_10000.csv")
    logger.info("Dataset with risk scores and premiums saved to data/preprocessed_data/processed_dataset_with_risk_scores_10000.csv")
    print("Dataset with risk scores and premiums saved to data/preprocessed_data/processed_dataset_with_risk_scores_10000.csv")
    logger.info("Training and evaluation completed.")
    print("Training and evaluation completed.") 

if __name__ == "__main__":
    main()