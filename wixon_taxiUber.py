import pandas as pd
import time
from scipy import stats
from datetime import datetime as dt
import numpy as np
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm


  
# days is a dict which converts datetime's numerical day of the week to a text based day of the week to be human understandable
days = {6: "Sunday", 0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday"}

#reads the data set you're pulling from, should be updated with each new input file usecols here only pulls certain named columns from the input file which helps the programs run a LOT faster. NOTE: the column names will have to change depending on the input file (because the folks who collect the data sometimes change the names of variables between data sets), please check the input file first!!!    

#dataIn = pd.read_csv("~/Downloads/yellow_tripdata_2010-08.csv", usecols=["tpep_pickup_datetime", "tpep_dropoff_datetime", "trip_distance"])


#this separate dataIn function is used for fhv data as we only collect the pickup date there
dataIn = pd.read_csv("~/Downloads/fhv_tripdata_2018-04.csv", usecols=["Pickup_DateTime"])



#this is a function for aggregating important variables by weekday and time
def taxiStats(data):

    #timeCars is a dict which holds relevant variables for each day and time such as travel time, travel distance, number of vehicles on the road, it can be modified in later code to add new different variables if needed
    timeCars = {}
    
    #timer to check how long processes take
    start = time.time()

    #While manually searching the data I learned that some data sets contain dates that are NOT within the specified period (e.g. January 20120 may get mixed into an input data set for August 2017). So I perform this check to determine what the year and month ought to be for the data set by checking that they are identical at 3 points
    if str(data.loc[round(len(data)*0.25), "tpep_pickup_datetime"])[0:7] == str(data.loc[round(len(data)*0.5), "tpep_pickup_datetime"])[0:7] and str(data.loc[round(len(data)*0.25), "tpep_pickup_datetime"])[0:7] == str(data.loc[round(len(data)*0.75), "tpep_pickup_datetime"])[0:7]:
        
        yearCheck = str(data.loc[round(len(data)*0.25), "tpep_pickup_datetime"])[0:7]
        
    else:
        return "Wrong Year/Month at 3 point check of file"


    firstWkDay = dt.strptime( (yearCheck+"-01"), '%Y-%m-%d').weekday()
    month = yearCheck[5:7]
    year = int(yearCheck[0:4])
    
    # "Thirty days hath September..." to get the average number of cars on a given weekday I have to know the number of each weekday in a month. So I use the number of days in the month and the initial weekday to calculate that. The code follows the old 
    if month == '09' or month == '04' or month == '06' or month == '11':
        dayinMo = 30
        
    elif month == '02':
        if year % 4 == 0:
            dayinMo = 29
        else:
            dayinMo = 28
    else:
        dayinMo = 31
        
    
    

    #for loop processes the whole input file or a subset, the first two lines pull out the date of the taxi fare and the hour it begins at. These are later used for the key
    for i in range(0, len(data)-1):
    
        #this if statement checks to make sure the year and month match with the pre-specified one obtained with the 3 point check
        if yearCheck == str(data.loc[i, "tpep_pickup_datetime"])[0:7]:
            day = days[dt.strptime(data.loc[i, "tpep_pickup_datetime"], '%Y-%m-%d %H:%M:%S').weekday()]
            hour = int(str(data.loc[i, "tpep_pickup_datetime"])[11:13])
            
            #the following if then series determine the total number of each weekday in a given month so that we can figure out the average number of cars which take fares on that given day
            if dayinMo == 30:
                if day == firstWkDay or day == firstWkDay +1 or day == firstWkDay-6:
                    totWkDays = 5
                else:
                    totWkDays = 4
            elif dayinMo == 31:
                if day == firstWkDay or day == firstWkDay +1 or day == firstWkDay-6 or day == firstWkDay +2 or day == firstWkDay-5:
                    totWkDays = 5
                else:
                    totWkDays = 4
            elif dayinMo == 29:
                if day == firstWkDay:
                    totWkDays = 5
                else:
                    totWkDays = 4
                    
            else:
                totWkDays = 4   
 
 #this if/else establishes travel time in minutes or "minTrav" by stripping out the hours minutes and seconds from the dropoff and pickup times and then subtracting pickup from dropoff. The else case handles what happens if a fare is picked up before midnight and droppoed off AFTER midnight so it doesn't appear there were 24 hours of travel in between   
            if int(str(data.loc[i, "tpep_pickup_datetime"])[8:10]) == int(str(dataIn.loc[i, "tpep_dropoff_datetime"])[8:10]):
    
                minTrav = round((int(str(data.loc[i, "tpep_dropoff_datetime"])[11:13])-hour)*60 + (int(str(data.loc[i, "tpep_dropoff_datetime"])[14:16]) - int(str(data.loc[i, "tpep_pickup_datetime"])[14:16])+ (int(str(data.loc[i, "tpep_dropoff_datetime"])[17:19]) - int(str(data.loc[i, "tpep_pickup_datetime"])[17:19]))/60))
        
            else:
                minTrav = round((int(str(data.loc[i, "tpep_dropoff_datetime"])[11:13]) + 24 -hour)*60 + (int(str(data.loc[i, "tpep_dropoff_datetime"])[14:16]) - int(str(data.loc[i, "tpep_pickup_datetime"])[14:16])+ (int(str(data.loc[i, "tpep_dropoff_datetime"])[17:19]) - int(str(data.loc[i, "tpep_pickup_datetime"])[17:19]))/60))


        #later I go on to calculate speed using distance and time, sometimes taxi drivers have <1 minute of travel time and this introduces divide by zero errors so I set a floor of 0.1 minutes in cases where travel appears to be instantaneous
            if minTrav == 0:
                minTrav = 0.1

        #the following are variables I'm interested in addition to "minTrav". "dist" is just the distance traveled in miles. "mph" is miles traveled per minute. "hourday" is a combination of hour by a 24 hour clock and the day of the week
            dist = int(data.loc[i, "trip_distance"])
    
            mph = round(dist/minTrav, 3)*60
    
            hourday = str(hour)+str(day)
    
            #print(dist, minTrav, mph)
        
        
            #here I build the dictionary of 24 hour periods over a 7 day week, each key is in the format "hourday" so midnight monday would be "0Monday" while 6 PM Friday would be "18Friday". If the key is already in the timeCars dictionary, then we add another car, the "dist" it traveled, the "minTrav" it was on the road, and the "mph" speed it was traveling at. If it's not currently in the dictionary we ad its initial values. 
            if hourday in timeCars:
                timeCars[hourday] = (timeCars[hourday][0]+1, timeCars[hourday][1]+dist, timeCars[hourday][2]+minTrav, timeCars[hourday][3]+mph, timeCars[hourday][4])
        
            else:
                timeCars[hourday] = (1, dist, minTrav, mph, totWkDays)
        
            #this code is in case I use a while loop to terminate on a specific date as opposed to after a certain number of iterations
            #i = i +1
            


    #this converts the dictionary from sums to averages by dividing every variable by the total number of cars under a given key. It's pretty fast since 7*24=168.    
    for key in timeCars:
        timeCars[key] = (timeCars[key][0]/timeCars[key][4], timeCars[key][1]/timeCars[key][0], timeCars[key][2]/timeCars[key][0], timeCars[key][3]/timeCars[key][0])
    
        #this code reports the number of seconds the code took to run and the number of rows in the data file
    end = time.time()
    totalTime = end - start
    print("time: ", totalTime, "input length: ", len(data))
    
    
    dataOut = pd.DataFrame.from_dict(timeCars, orient='index', columns=["TotalTaxis", "MilesTraveled", "MinutesTraveled", "MPH"])
    
    dataOut.to_csv('~/Documents/pythonpractice/taxiDataOut.csv') 
        
    return(dataOut)





# the function fhvStats is similar to the prior function taxiStats in nearly every way, except there's less data available for the FHV files: we only track the number of uber/lyft type vehicles on the road, not distance, travel time and speed data. Therefore I've left the comments out of this function as they would be nearly identical to the prior comments in the taxiStats function
def fhvStats(data):

    FHV = {}
    
    if str(data.loc[round(len(data)*0.25), "Pickup_DateTime"])[0:7] == str(data.loc[round(len(data)*0.5), "Pickup_DateTime"])[0:7] and str(data.loc[round(len(data)*0.25), "Pickup_DateTime"])[0:7] == str(data.loc[round(len(data)*0.75), "Pickup_DateTime"])[0:7]:
        
        yearCheck = str(data.loc[round(len(data)*0.25), "Pickup_DateTime"])[0:7]
        
    else:
        return "Wrong Year/Month at 3 point check of file"


    firstWkDay = dt.strptime( (yearCheck+"-01"), '%Y-%m-%d').weekday()
    month = yearCheck[5:7]
    year = int(yearCheck[0:4])
    
    if month == '09' or month == '04' or month == '06' or month == '11':
        dayinMo = 30
        
    elif month == '02':
        if year % 4 == 0:
            dayinMo = 29
        else:
            dayinMo = 28
    else:
        dayinMo = 31
    
        
    
    for i in range(0, len(data)-1):
    
        if yearCheck == str(data.loc[i, "Pickup_DateTime"])[0:7]:
            day = days[dt.strptime(data.loc[i, "Pickup_DateTime"], '%Y-%m-%d %H:%M:%S').weekday()]
            hour = int(str(data.loc[i, "Pickup_DateTime"])[11:13])
            
            if dayinMo == 30:
                if day == firstWkDay or day == firstWkDay +1 or day == firstWkDay-6:
                    totWkDays = 5
                else:
                    totWkDays = 4
            elif dayinMo == 31:
                if day == firstWkDay or day == firstWkDay +1 or day == firstWkDay-6 or day == firstWkDay +2 or day == firstWkDay-5:
                    totWkDays = 5
                else:
                    totWkDays = 4
            elif dayinMo == 29:
                if day == firstWkDay:
                    totWkDays = 5
                else:
                    totWkDays = 4
                    
            else:
                totWkDays = 4   
    
            day = days[dt.strptime(data.loc[i, "Pickup_DateTime"], '%Y-%m-%d %H:%M:%S').weekday()]
            hour = int(str(data.loc[i, "Pickup_DateTime"])[11:13])

            hourday = str(hour)+str(day)
   
            
            if hourday in FHV:
                FHV[hourday] = (FHV[hourday][0]+1, FHV[hourday][1])
            else:
                FHV[hourday] = (1, totWkDays)

    for key in FHV:
        FHV[key] = (FHV[key][0]/FHV[key][1])


    dataOut = pd.DataFrame.from_dict(FHV, orient='index', columns=["Uber/Lyft"])
        
    dataOut.to_csv('~/Documents/pythonpractice/FHVDataOut.csv') 
        
    return(dataOut)
    

# I've taken the liberty of doing some sorting and compiling of output files produced with taxiStats() and fhvStats() using spreadsheet software (LibreOffice Calc). I assure you can I do these operations in Python as well, but it was faster/easier to do them in an Excel equivalent if I'm only doing them once. I intend on using the most appropriate tools for the job regardless how glamorous (or inglamorous) they might be. 
masterOut = pd.read_csv("~/Documents/NYCTaxiFHVMasterOutput.csv")

# assortedStats is a small set of statistics operations performed to yield the output
def assortedStats(data):
    Aug2017MPH = masterOut.loc[:, "Aug2017MPH"]

    Apr2011MPH = masterOut.loc[:, "Apr2011MPH"]

    #tTestMPH runs a paired samples T Test comparing the average speed of Yellow Cab taxis in August 2017 to April 2011. It returns a T Statistic and a siginificance. If the significance is p < 0.05 then we can judge that the two compared samples are significantly different (or are at least 95% likely to be significantly different). The actual value may be *more* significant since each row is the average for a given weekday and hour (e.g. Tuesday at 8PM) and contains within it hundreds to thousands of fares: I'm saying we have an artificially low sample size because I aggregated this to make it easily readable. 
    tTestMPH = stats.ttest_rel(Aug2017MPH, Apr2011MPH)

    print(tTestMPH)


    # I looked up how to get an effect size from the results of a paired samples t test, I corrected for correlation because these two factors are pretty correlated https://www.leeds.ac.uk/educol/documents/00002182.htm https://www.researchgate.net/post/How_can_I_calculate_the_effect-size_for_a_repeated_measures_t-test
    correlMPH = stats.pearsonr(Apr2011MPH, Aug2017MPH)

    SD_Pooled = np.sqrt(np.std(Apr2011MPH)*np.std(Apr2011MPH)+np.std(Aug2017MPH)*np.std(Aug2017MPH))/2

    PearsonDUncorrected = (np.mean(Aug2017MPH)-np.mean(Apr2011MPH))/SD_Pooled

    PearsonDCorrected = (PearsonDUncorrected/correlMPH[0])

    print("Corrected Effect Size = ", PearsonDCorrected)
    
    
fhvStats(dataIn)

