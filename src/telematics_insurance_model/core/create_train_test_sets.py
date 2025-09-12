import pandas as pd
from sklearn.model_selection import train_test_split


preprocessed_df = pd.read_csv("data/preprocessed_data/processed_dataset_10000.csv", sep=";")

# Target variable: monthly claims (binary)
y = preprocessed_df["Claim_this_month"]


# Extracting feature matrix, removing target column
X = preprocessed_df.drop(cols=["Claim_this_month"], axis=1)

# Split the training and testing data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

# Save the train and test sets
train_set = pd.concat([X_train, y_train], axis=1)
test_set  = pd.concat([X_test, y_test], axis=1)

train_set.to_csv("data/preprocessed_data/train_set_10000.csv", sep=";", index=False)
test_set.to_csv("data/preprocessed_data/test_set_10000.csv", sep=";", index=False)

print("Train and test sets created and saved to data/preprocessed_data/")
print(f"Train set shape: {train_set.shape}, Test set shape: {test_set.shape}")
