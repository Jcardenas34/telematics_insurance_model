
# Introduction
Hello, my name is Juan Cardenas, and I applied for the position of AI Associate because I beleive it is a great first step
in the development of my career as an AI engineer. 

In my submission, I was able to clean and process and existing dataset of auto insurance claim data to have it include
additional features, as well as telematics data so I could train a logistic regression algorithm that would price auto policies more fairly by taking into account 
driver behaviour. I also simulated accelerometer telematics data to simulate a real 10 minute trip for both good and bad drivers, this data is able to be evaluated
by my trained algorithm and can eventually be used to feed to an algorithm in real time.

# General Goal
My goal was to create a logistic regression algorithm to predict the probability of a claim being filed in a given month from policy holder data.
This includes both traditional demographic data, as well as telematics data that I simulated. The output of the algorithm would be a factor ranging from 0 to 1
that would indicate a "risk_factor" which would then be used in a simple dynamic pricing model. here 

$$ monthly\_premium = base\_premium + \alpha*risk\_factor $$

Where monthly premium equals a base premium plus a maximum penalty factor alpha multiplied by the risk factor.
So when risk factor decreaces due to good driver habits, this can be reflected in the monthly premium and vice versa.
Making for a more enjoyable customer experience.

# Approach
I began by taking the existing claim data with 100k entries, which had 1 entry per year of coverage and spanned over 3 years.
Where the number of claims in that year was present.
Since my goal was to create a logistic regression algorithm that would calculate risk on a monthly basis, I decided to
break a single row into 12 rows, and distribute the number of claims randomly between the months, counting these as instances where bad driving occoured.

From here, I simulated telematics data by drawing adverse driver events such as speeding events, hard, breaks and hard accelerations, by
modelling them using a poisson distribution with higher means for bad driver behaviour. This emulated and correlated driver behaiour with months that had claims.

# Model selection and evaluation
My immedeate approach given the time constraints was to select the simplest model and use it as a baseline using both traditional and telematics data.
From there i would move on to more complex models if necessary.

I began with a logistic regressor in scikit learn and trained on 120k months of driver records.
Where months without a claim represented a vast majority of the events in the set. 
I trained models with traditional data only, telematics data only and with both traditional and telematics data.

The performance of the algorithms was rather good when using AUC metrics, ranging from .88 using only trraditional features
and .98 when including telematics data. But with a precision for the positive class was .33 at maximum, indicating a high false positive rate.
and a potential skew towards higher prices for good drivers.

Given this good performance I decided not to persue neural networks for the time being.


I now wanted to quantify the effect that using different models had on the average premim for good drivers and I found that good drivers 
saved on average $37 per month when using the model that included telematics data. this can be seen more in depth in the 
'how risk reflects premium' jupyter notebook.


# Real time data processing
From here, I decided to simulate accelerometer data for real time processing.

I was able to simulate a 365 10 minute drives at neighborhood speeds with good and bad driver behaviour by simulating accelerometer and velocity readings
and using those values to count the number of adverse events.

These adverse events are then be tallied and stored in a csv file for use as input to my logistic regression algorithm to calculate risk. that pipeline can be run by running 

	generate-telematics

followed by

	evaluate-generated-telematics


Where images of the accelerometer data and averse events per trip are shown in the figures file.

# Summary

In summary I developed a code base to show a proof of concept for a logistic regression algorithm that takes into account driver behaviour and shows that it can have a material effect on pricing. Rewarding drivers with lower premiums when they drive more safely. I was also able to simulate accelerometer data for telematics that will be used in a live input system, as well as shows trip data for a given driver. See figures folder 

















