

GitHub repo: https://github.com/Jcardenas34/telematics_insurance_model/tree/main

# Setup, run, and evaluation steps:
Here is a brief description of how to reproduce results of the analysis
Full description of steps and methodologies can be found at 
https://github.com/Jcardenas34/telematics_insurance_model/tree/main
https://github.com/Jcardenas34/telematics_insurance_model/blob/main/notebooks/how_risk_reflects_premium.ipynb


# Setting up the repo
    Setup of this code base is simple create a virtual environment, clone this repo, install the package and run steps.

    conda create -n telematics python=3.11

    conda activate telematics

    git clone git@github.com:Jcardenas34/telematics_insurance_model.git

    cd telematics_insurance_model

    pip install -e . 


# Quickstart
    Once setup simply run the following lines as is to produce results. Look in figures, logs, data, etc to view work.

    create-preprocessed-data
    train-logistic-regressor

    generate-telematics
    evaluate-generated-telematics




# Any notes on models, data, or external services.
    Models: logistic regressors via scikitlearn trained on traditional, telematics and traditional+telematics data.
    Data: used https://data.mendeley.com/datasets/5cxyb5fp4f/2 as a basis, and appended simulated telematics data to it
    External services: Google, Claude, ChatGPT, Github Copilot (all free unpaid versions). 

A full description on models, approach, data and external services can be found in 
https://github.com/Jcardenas34/telematics_insurance_model/tree/main

