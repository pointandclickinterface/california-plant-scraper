# Los Angeles Native Plant Analyzer

This program builds off of the California Native Plant scraper to organize the plants the scraper finds to suggest native plants based on zipcodes in Los Angeles .

There is a folder in src that has sample outputs in it for Santa Monica, California.
##Updates to Scraper

Scraper now includes timeouts on all requests to prevent hanging requests on long calls

## Maintainability 

This program was built on Python 3.6 and will run on Python 3.8.5.
It is known to run on Mac and Linux.

# Requirements

In order to use this program you will need the following packages:
    - bs4
    - tqdm
    - pandas
    - matplotlib
    - numpy
    - requests

You will need to have the src folder and the data folder in the same parent directory to run static mode.

## Functionality

The Los Angeles Native Plant Suggester can run in static mode where it demos three different zipcodes. 
It runs three different filters to make three different graphs.

# Running the analyzer

** Default Mode **

    In default mode the scraper will pick a random zipcode in LA and gather plants in the zipcode.
    It will then output csvs and figures of its findings.
    To run this type from the src directory:
        `python3 native_plant_analyzer.py`

    ** Warning **
	This can take up to half an hour as some zipcodes have hundreds of plants to scrape.

** Static Mode **

    To see the premade data run for three different zipcodes run from the src directory:
        `python3 native_plant_analyzer.py --static`

    Please keep src folder and data folder in the same parent directory for this to run.

    It will output a butterfly garden figure and csv for Larchmont, a csv and figure of succulents for Malibu, and a csv and figure of Full Sun Flowering Shrubs for Boyle Heights.
    

## Extensibility

In the future I might add the option to enter a zipcode in the commandline to have it preform analysis on that and expand the reach to all of California.


