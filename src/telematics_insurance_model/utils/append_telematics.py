
import pandas as pd
import numpy as np


def append_telematics(dataframe: pd.DataFrame) -> pd.DataFrame:

    '''
    Expands the input dataframe by creating 12 rows per driver-year, one for each month.
    Each month is assigned a binary target variable "Claim_this_month" based on the annual claim
    frequency "N_claims_year". Telematics features are simulated based on whether a claim
    occurred that month.
    Args:
        dataframe (pd.DataFrame): Input dataframe with driver-year level data.
    Returns:
        pd.DataFrame: Expanded dataframe with monthly data and simulated telematics features.

    '''
    np.random.seed(42)
    expanded_rows = []


    for _, row in dataframe.iterrows():
        # get claim frequency for this driver-year
        n_claims = row["N_claims_year"]

        # probabilistic monthly claim assignment
        # monthly probability = n_claims / 12
        # monthly_claims = np.random.binomial(1, n_claims / 12, size=12)
        if n_claims > 12:
            n_claims = 12
        claim_months = np.random.choice(12, n_claims, replace=False)
        monthly_claims = [1 if m in claim_months else 0 for m in range(12)]


        for month in range(1, 13):
            new_row = row.copy()
            new_row["Month"] = month
            new_row["Claim_this_month"] = monthly_claims[month - 1]

            if monthly_claims[month - 1] == 1:
                # Claims will be correlated to bad driving, high average speed
                # hard brakes, and acceleration, and high speeding events.
                
                # Averate speed of trip is normally distributed, neigborhood driving at 10 mph over limit, 40mph
                new_row["avg_speed"] = np.random.normal(40, 10, size=1)[0]   # mph
                new_row["hard_brakes"] = np.random.poisson(2, size=1)[0]     # counts
                new_row["hard_accel"] = np.random.poisson(2, size=1)[0]     # counts
                new_row["speeding_events"] = np.random.poisson(2, size=1)[0] # counts
                # Average commute time is 20 mins
                new_row["trip_len"] = np.random.normal(35, 10, size=1)[0] # counts

            else:
                # Averate speed of trip is normally distributed, neigborhood driving at 30mph
                new_row["avg_speed"] = np.random.normal(25, 10, size=1)[0]   # mph
                
                new_row["hard_brakes"] = np.random.poisson(1, size=1)[0]     # counts
                new_row["hard_accel"] = np.random.poisson(1, size=1)[0]     # counts
                new_row["speeding_events"] = np.random.poisson(1, size=1)[0] # counts
                # Average commute time is 20 mins
                new_row["trip_len"] = np.random.normal(20, 10, size=1)[0] # counts

            expanded_rows.append(new_row)

    monthly_dataframe = pd.DataFrame(expanded_rows)

    return monthly_dataframe

