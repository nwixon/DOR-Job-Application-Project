wixon_taxiUber.py README

The following program was written for Python 3.5, it will likely fail to run if you attempt to compile it in a different version.

There are 3 functions in this program: 

taxiStats() - Begins at line 25, concludes at line 138. On my system it takes approximately 30 minutes to process an input taxi csv from http://www.nyc.gov/html/tlc/html/about/trip_record_data.shtml this should process that csv into a more organized format. It reads all rows of the input csv, drops any rows that aren't for the specified month & year (because I've found files that have errors) and then calculates averages for each weekday and hour. It starts with 0Tuesday which is the number of taxi fares taken within the hour of 12 AM on Tuesday averaged across every Tuesday in the month. It also includes average travel time, distance traveled, and average speed in MPH. Please note that each csv file MAY have slight variations in the labels for each variable so the variable names may need to be changed to match. It saves a CSV file to disk and you may need to change the path for that. 

fhvStats() - Begins at line 145, concludes at line 218. This is essentially a stripped down version of taxiStats() which only reports the average number of FHVs which accepted fares at each hour. It is not commented, as such comments would be redundant given all the comments in taxiStats().

assortedStats() - Begins at line 225, concludes at line 245. This function takes an input that is basically just a combination of the output files from taxiStats() and fhvStats(). I did some of the re-sorting and copy pasting in LibreOffice Calc (Linux's equivalent of Excel) because it was particularly "quick and dirty" as specified, and saved on a large body of additional code for you to read through. I assure you I can add code to do all these operations if you'd like, in lieu of that I've included the edited file comprised on those outputs. 

assortedStats() just includes some code for a paired samples T-Test and some code to get the effect size of that T-Test. 
