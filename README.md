# nlb-scrape
New Lantao Bus Company provides an [API](https://data.gov.hk/en-data/dataset/nlb-bus-nlb-bus-service) through [data.gov.hk](https://data.gov.hk/). They provide a route list, stops for a route, and ETA for stops, but not a timetable for each route. They do have these timetables available on their [website](http://www.newlantaobus.com/), so I created this project to scrape the timetables from there.

Route List is obtained from their API. Scraper iterates through the route IDs and the relevant website URL then scrapes the timetable.

## Usage

Install the required packages:
```pip install beautifulsoup4```

Run

```python daysDictionary.py```

daysDictionary builds the daysDictionary json file.  
Each entry in the array has a serviceDaysString which is taken from the heading of each table in HTML.  
You're free to define the string with the other key-value pairs, but for me I start the week on Monday so for a service string of:  
  
"Monday to Friday", I define ```dayStart``` as 0 and ```dayEnd``` as 4.

```python scrapeNLB.py```

## JSON

Json structure matches the one used in my [https://github.com/pkboy/sunferryhktimetable](https://github.com/pkboy/sunferryhktimetable) project that converts that data from CSV to JSON.

## Issues

- Data from timetables where stop information is not in a standard format will be erroneous, such as circular routes where departures are presented as a time period with the route's headway time.
- Data is in English but can be set to Traditional and Simplified Chinese, see comments.

## Contributors

[pkboy](https://github.com/pkboy/)