# Integrating Telematics Data Into A Dynamic Pricing Model
This repo shows the development of a fair pricing auto insurance model using Machine learning to factor in driving habits into customer insurance pricing.
Materially lowering insurance premiums for good driving habits.

# Setting up the repo
Setup of this code base is simple
Create a virtual environment, clone this repo, install the package and run steps.

```
conda create -n telematics python=3.11

conda activate telematics

git clone git@github.com:Jcardenas34/telematics_insurance_model.git

cd telematics_insurance_model

pip install -e . 
```

# Quickstart
Once setup simply run the following lines as is to produce results. Look in figures, logs, data, etc to view work.

```
create-preprocessed-data
train-logistic-regressor

generate-telematics
evaluate-generated-telematics
```

# Dataset
The dataset used in this analysis was taken from mendeley data [^label], and contains a span data from three full years (November 2015 to December 2018) concerning non-life motor insurance portfolio. This dataset comprises 105,555 rows and 30 columns. Each row signifies a policy transaction, while each column represents a distinct variable. As it stands, no telematics data was included in the dataset. To simulate good and bad driver behaviour over the course of 365 trips (simulating a year of daily driving) use 'create-preprocessed-data'. 

```
[^label] Lledó, Josep; Pavía, Jose M. (2024), “Dataset of an actual motor vehicle insurance portfolio”, Mendeley Data, V2, doi: 10.17632/5cxyb5fp4f.2
```
https://data.mendeley.com/datasets/5cxyb5fp4f/2



# Generate telematics driver data 
To append telematics data to the dataset for both good and bad driver behaviour, simply run
```
create-preprocessed-data
```
from the top directory.




# Dynamic pricing model

In order to asess a driver's risk in a way that will inform thier monthly premium,
I have chosen a pricing scheme that is a function of a calculated "risk_factor", which is determined via a logistic regression algorithm. The dynamic pricing model is as follows. 


$$premium = base\_rate + \alpha*risk\_factor $$
Where 
$$ BaseRate = \$300, \alpha = \$200 $$
and
$$ 0 \leq risk\_factor \leq 1 $$
 a higher risk factor, determined by customer demographic information as well as driver behaviour (telematics), will be reflected in the monthly premium and updated after each risk asessment (drive). 



# Risk Asessment
A logistic regression algorithm is used to determine weather a claim will be filed within a given month due to traditional risk factors as well as drivor behavour (telematics). By running

    train-logistic-regressor

3 models will be trained, one using only traditional demographic factors such as __, one using only telematics features such as number of speeding events, hard breaks, etc. and one using both traditional and telematics features. And are stored in the \models directory.

# Model Performances
When training using 120k months of driver data, the logistic regression models performed in the following way. Features are defined in [feature_selection.py](/src/telematics_insurance_model/helpers/feature_selection.py)
```
* Using traditional features only *
ROC-AUC: 0.8883
Classification report:
              precision    recall  f1-score   support

           0       0.99      0.83      0.90     34819
           1       0.13      0.76      0.22      1181

    accuracy                           0.83     36000
   macro avg       0.56      0.79      0.56     36000
weighted avg       0.96      0.83      0.88     36000
```
```
* Using telematics features only*
ROC-AUC: 0.9643
Classification report:
              precision    recall  f1-score   support

           0       1.00      0.90      0.95     34819
           1       0.24      0.90      0.37      1181

    accuracy                           0.90     36000
   macro avg       0.62      0.90      0.66     36000
weighted avg       0.97      0.90      0.93     36000
```

```
* Using traditional + telematics features *
ROC-AUC: 0.9826

Classification report:
              precision    recall  f1-score   support

               0       1.00      0.94      0.97     34819
TODO           1       0.33      0.93      0.48      1181

    accuracy                           0.94     36000
   macro avg       0.66      0.93      0.73     36000
weighted avg       0.98      0.94      0.95     36000
```

# Affect of Telematics data on final premium
In summary, good drivers save on average $37 when telematics data to inform monthly premiums. Bad drivers pay on average $37 more. The analysis is detailed extensively in [how_risk_reflects_premium.ipynb](/notebooks/how_risk_reflects_premium.ipynb) 

![difference_in_premium_when_using_telematics](/figures/difference_in_premium_when_using_telematics.png)


# Generating accelerometer telematics data for real time pricing 
To generate accelerometer data for use in a real time streaming application run 

    generate-telematics

This will generate 365 simluated driving trips for both good and bad driver behaviour. It also adds additional variables related to age and driving experience, and removes any features not needed for training. This data is then stored in 'data/preprocessed_data' to use as input to logistic regression algorithm for risk asessment, as well as part of the pipeline to process data in real time. A sample of the metrics shown and the measurement of the adverse events is shown below. 

**Here an a speeding event is one where the driver is going over the speed limit for longer than 3 seconds.**

## Good driver dashboard for trip
![good_driver](/figures/GOOD_DRIVER_001_GOOD_TRIP_001.png)



## Bad driver dashboard for trip
![bad_driver](/figures/BAD_DRIVER_001_BAD_TRIP_001.png)

# Evaluating Telematics data

An evaluation pipeline using the trained models has been started and can be run using

    evaluate-generated-telematics

This will calculate a new risk factor based on the number of adverse events experienced in the given trip. These adverse events can then be tallied up throughout the month (62 trips)to give a risk asessment and final premium price.  