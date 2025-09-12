


# Strategize
	Ok, so I realize that Im not going to be able to do this right away.. I need to think about a few things...

	So.. create a pricing model for the 

	So for the company to make money, on insuance, they need to collect more money than they payout in insuance premiums

	And so.. 

	if we have data, on how much money a given person filed in claims per year and with different attributes.
	We can see which are the most at risk drivers, as well as decide on a amount of money that is needed in order 
	to still make a profit, this can determine our base payment.

	from there, if we can predict how much money a person will cost us given input variables, we can set the insurance cost
	to eb x% above this to recoop costs. We can then take into account driver behaviour into this calculation, and price appropriately.

	The thing is.. we want to asess the risk score in real time?? 

	And so, we can determine a min price that is needed to charge, based on the average cost and number of customers

	They said that I need to have a risk score associated with heach policy holder. 


	I guess.. The way that I can do this is by looking at how much a given customer was charged in terms of premiums, 
	and see where they lie on the z distribution. 


	so all I know is that higher accerlerometer data will have to lead to a higher risk score.


	Ideally, I would have data for driver demographics as well as telemetrics data, but here I dont have that..
	
	I have found a dataset that DOES have the driver data, but is missing the telemetrics data..
	So what do I do with this.. So.. right now, In order to create a model, I have to create either a supervised, or 
	unsupervised model. 
	
# Deciding on how to measure risk

	The thing is.. what do I want to predict here.. risk?? and see how that factors into the end product?
	OR do I want to try and predict insurance premium, or what?

	I dont think I want to directly calculate the insurance cost to the user. although thats what they will pay attention
	to in the end.. 

	But.. I guess if I can use regression to calculate a risk score, then I can use that to calculate the pricing.

	So I will see how the addition of data will affect the risk, and how the risk will affect rpicing in the end.

	so I have seen this formula..

	premium = base_cost + (a*risk_factor)

	if risk factor goes from 0 to 1 as in logistic regression.. then we will fluctuate in cost around.

	base_cost+- a at maximum..

	So.. I need to create a model that will predict risk score, but not only that It will predict it in real time.

	I guess that is possible if it takes in the telemetry data while the other data are fixed, or are updated
	on a slower basis, like total_claims_this_year, average_claims_per_year would also be useful..

	So.. I am back with this logistic regression problem..

	So.. based off of this..
	https://pmc.ncbi.nlm.nih.gov/articles/PMC11386000/#_ad93_

	I can make a model that will predict weather someone will file a claim. and if they do, their risk score will go up.

	So.. this is actually, maybe a good thing since, that is what would drive the cost of insuring a person.

	I can model this as, probability that someone will file a claim as the risk score, this lends itsself to logistic 
	regression. And once they do file a claim , I guess thier base can go up, and the driving behaviour will influence 
	how much thier premium goes up or down, so they sill have control over thier premium, but 

	Ok, so.. how can I determine the probability that they will file a claim? And produce a risk score from this?

	I guess I dont want perfect.. I just want a model that incorporates everything..

	I guess, this should also be an 'at fault claim' since otherwise the claims will raise theier insurance for no reason..

# Exploration of dataset

	So.. does the dataset I have allow me to calculate the probability of a claim being filed? 

	Age, location, vehicle type, past claims?
	The dataset has: Age of driver, number of years driving, cost of claims (indicates severity of the claim),
	n_claims_year, n_claims_history, R_claims_history, type_risk (roughly corresponds to vehicle type), Area (traffic _condistions)
	second_driver (more people driving means more risk), vehicle_characteristics (maybe type of vehicle increaces probability of collisions)

	So.. I want to see if these variabels are highly correlated with the number of claims, or collisions..
	but how do I do that..

	And from here, I want to be able to have just 1 value per account? Now I have data for a given year.
	Can I use the data for each year as a training datapoint? I guess years are independent of each other.

	I need to know, how these variables correlate to.. N_claims_year. this would I guess.. give an indication
	of weather a customer filed a claim. But.. some have up to 9 claims in a year.. So.. do I just convert this to binary?
	for no claim to any number of claims? I guess claim history is where this would come into play.. hisgher claims
	in the past, could predict higher claims in the present.

	Once I calculate a risk score for each person.. by creating a logistic regression model. I can add in driver 
	telemetrics data.. Since the current risk score only took into account vehicle type and other characteristics.
	I can assume that driving behaviour is gaussian amongst age ranges.. And leave the claim logistic regression
	model unchanged? This will then change the model to take into account driving behaviour.. even though its 
	not the actual driver behaviour. we can then invect artifical driving data to see how this would affect premiums in the end.

	
# Including telemetrics data

    So, once I have the tradiational datasets.. how would I incorporate the telemetrics data??

    The requirements are for the pricing to change in real time according to the driving behaviour

    lets just say that the pricing model is based on 

    premium = base_rate + (a*risk) + factors

    What kinds of telemetrics data can I incorporate??

*    speed
*    braking patterns
*    mileage
*    time of travel
*    and geolocation.

    How can I normalize these so that they can become training variables?

    The usual is to create gaussians from them, can I do that?
    I also need this to be a real time evaluation system, not something that I can calculate
    once 

    So.. this will indicate PRESENT risk, like at this very second risk.. but not.. risk that comes 
    from the driving history.. 
    well.. first let me find a telemetrics data, and see if I can just attatch this behaviour to all othe other drivers..

    But...I need to be able to gather information from the trips and add them to a long term stable dataset.
    Where the behaviour is recorded.. like perpleity suggested, monitor the driving behaviour for number of hard 
    breaks per day? number of speeding events per day?

    The thing is.. that since those tradiational factors are being measured on a yearly basis.. how will
    I mix them with monthly premiums? 

    Yeah I guess I would have to tally up the number of risky events per month, and then pass them to the model to evaluate risk at the end of the month and 

    But.. we can create display of how real time behaviour affects price. But.. I guess the behaviour resets at the end of the month? and the driver has the opportunity to lower thier cost by driving well.

    So.. with good behaviour, the price will stay at a baseline risk associated with the vehicle they are driving and age.

    I need to be smart about how I assign driving behaviour to the people.. since assigning a good driving 

    I mean I could also make this a factor in the model, where the good driver score could range from -1 to 1 
    and increace or decreace the cost by a certain maximum amount..

    either that OR I could bake this striaght into the initial model that calculates risk..
    if thats the case then I cant use a risk score from 0 to 1 can I 

    yeah I can either have the driving behaviour be correlated to the tradiational characteristics, or
    be indiependent and add it as a factor.. 

    I guess the model can start off at the lowest rate, and then increace as the model detects bad driving behaviour.
    But once the event is detected it permanantly changes the monthly price.


    The model in this case would be very simple.. you get a discount for no adverse events, and a linearly 
    increacing price increace for each adverse event. where each event has a negative price associated with it


    I guess through that I would have to necessarily correlate bad driving risk with the probability of getting a claim..

    So.. I guess I can sort poilcy holders by the number of claims, and give them a bad driving habits.


    The dirving habits could be incremented in real time. and pushed to the algorithm..

    As long as I prodce something..


    I actually could wrap up the adverse events in the initial model if I create a dataset 
    that includes those as synthetic data. so that theyre automatically correlated with the number of 
    claims.

    The thing is.. the dataset that I have is for the number of claims in a year, not a month..
    So.. I need to find a dataset that has these on the same basis...

    I guess since this is a synthetic dataset.. I can adjust the data so that..

    the number of claims gets incremented.. that would expand the dataset forsure..


    So. N_claims per year = 3 would be broken into 3 instances.  with a boolean value.

    I guess to actually break it into claims per year, I would have to break the entry into 12 months with 
    3 of the 12 having a claim, and the other 9 not having a claim. and associate the months with claims to have 
    bad driving behaviour. This would eliminate the bias for certain demographic of people.

    I need the data to be euqlly represented as well.. across demographics.. or do I? I guess I need to frequency of measurement needs to be normalized. 

    But.. ok so I can do this.. 

    split each entry into a total of 12 entries, and divide up the claims into months randomly. 
    fuck though, one person got 25 claims in one year.. so how would I split that, thats like, 2 claims a month..
    I guess in that case I would just say there was a claim every month..

    And just associate bad behaviour for each month.

    I also have to associate bad driving behaviour even if no claims were made. But I guess..


    Ok so take each row in the dataset that has tradiational data.
    split the row into 12 and distribute the number of claims into the entries to indicate that a claim was made.
    This will determine risk factor. if above 12 then assign claim to every month.

    Then attatch driving behaviour variables to the list of variables like.

    Number of speeding events per month, number of hard breaks per month, and anything else I can determine 
    from the datasets that I have..

    So which telemetrics data am I going to use?

    I also have to model the driving behaviour off of the input data that I have..
    Like what is the ma and min of the adverse events,

*    the data will then be put into a logistic regression algorithm that will calculate risk..
    Either a neural net or a linear model, XGBoost?, How would decision trees work here? I guess it could 
    work the same since we want to output 0 to 1
    And then give a price indication afterwards when put through the formula.

    The algorithm can do a live risk asessment by streaming in the data and keeping track of the number of adverse events. After every drive, a model inference is called, and we can see how the data being monitoed affected
    the cost of the insurance.. No adverse events, no price increace.

    Integrate weather API into algorithm for risk asessment.

    



