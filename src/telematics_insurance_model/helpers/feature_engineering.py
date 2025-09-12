
import pandas as pd
from dateutil.relativedelta import relativedelta

def add_age_and_years_driving(df: pd.DataFrame) -> pd.DataFrame:
    '''
    '''

    # Reformatting date variables to determine driver age and numere of years driving  
    df['Date_birth'] = pd.to_datetime(df['Date_birth'], format='%d/%m/%Y')
    df['Date_driving_licence'] = pd.to_datetime(df['Date_driving_licence'], format='%d/%m/%Y')
    df['Date_last_renewal'] = pd.to_datetime(df['Date_last_renewal'], format='%d/%m/%Y')

    # Calculate driver Age and years licensed
    df['age'] = df.apply(lambda row: relativedelta(row['Date_last_renewal'], row['Date_birth']).years, axis=1)
    df['years_driving'] = df.apply(lambda row: relativedelta(row['Date_last_renewal'], row['Date_driving_licence']).years, axis=1) 

    return df