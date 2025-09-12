

telematics_features = [
    "avg_speed",
    "hard_accel",
    "hard_brakes",
    "trip_len",
    "speeding_events"
    ]


traditional_features = [
    "age",
    "Type_risk",
    "Second_driver",
    "years_driving",
    'N_claims_history', 
    'R_Claims_history',
    "N_doors",
    "Power",
    "Cylinder_capacity",
    "Value_vehicle",
    "Area",
    # "Type_fuel",
    # "Length",
    "Weight"
]

# These features are unneceessary for training
drop_arr = ['ID', 'Date_start_contract', 'Date_last_renewal', 'Date_next_renewal', 'Date_birth',
            'Date_driving_licence', 'Distribution_channel', 'Seniority', 'Policies_in_force', 'Max_policies',
            'Max_products', 'Lapse', 'Date_lapse', 'Payment', 'Premium', 'Year_matriculation']


all_feature_cols = telematics_features + traditional_features
