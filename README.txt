# Interest analysis by region using Pytrends and Places API

This project's objetive is to analyse the interest to availability ratio of a service using Pytrends and Google Maps, 
the purpose being market analysis as well as necessity analysis for a certain region.
The script returns:
- A scatter plot of interest vs. availability with lables
- A scatter plot of interest vs. availability without lables.
- A histogram for interest per location.
- A histogram for availability per location.

#interest_analysis.py
This is a commentated script that saves the plot as a pdf

#interest.py
This is a script inteded to be used as a Python library

Some considerations must be made before using this script

- Try different search parameters:
Sometimes you might get few results, or too many using Pytrends and Places. These are some suggestions to 
troubleshoot that: 
    - Use a more specific keyword (i.e. search chiropractor clinic instead of chiropractor)
    - Change search radius
    - Add, remove or edit parameters (limit results by price, ratings, etc.)
    - Make sure the script works using another word 
    
- Do this process in parts
I recommend doing this process in parts, so you can adjust your search parameters accordingly

- Pytrends might return 0 

- Not all regions are as effective
Not all regions and countries have the same amount of information, some countries return poor results and this
kind of analysis isn't useful. 

