import numpy as np
from scipy.stats import poisson


'''
Script to simulate telematics data

Driver behaviour in the logistic regression algorithm will be recorded in batches 
Driver metrics will be recorded on a per trip basis, and used to feed into alg.

So these are counts, and can be modeled from a poisson distribution


'''

# We expect 2 hard breaks from a driver during the average month
lambda_val = 2
sample_size = 100000
poisson_samples = np.random.poisson(lambda_val, sample_size)

std_dev = np.sqrt(lambda_val)
lower_tail_threshold = lambda_val - .5 * std_dev
upper_tail_threshold = lambda_val + .5 * std_dev

print(f"Lambda: {lambda_val}")
print(f"Lower tail threshold: {lower_tail_threshold:.2f}")
print(f"Upper tail threshold: {upper_tail_threshold:.2f}")

lower_tail_samples = poisson_samples[poisson_samples < lower_tail_threshold]
upper_tail_samples = poisson_samples[poisson_samples > upper_tail_threshold]

print(f"\nNumber of samples in lower tail: {len(lower_tail_samples)}")
print(f"Lower tail samples (first 10): {lower_tail_samples[:10]}")

print(f"\nNumber of samples in upper tail: {len(upper_tail_samples)}")
print(f"Upper tail samples (first 10): {upper_tail_samples[:10]}")