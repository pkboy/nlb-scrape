# nlb-scrape
New Lantao Bus Company provides an [API](https://data.gov.hk/en-data/dataset/nlb-bus-nlb-bus-service) through [data.gov.hk](https://data.gov.hk/). They provide a route list, stops for a route, and ETA for stops, but not a timetable for each route. They do have these timetables available on their [website](http://www.newlantaobus.com/), so I created this project to scrape the timetables from there.

Route List is obtained from their API. Scraper iterates through the route IDs and the relevant website URL then scrapes the timetable.

## Usage

Install the required packages:
```pip install beautifulsoup4```

Run
```python scrapeNLB.py```

## Issues

- Data from timetables where stop information is not in a standard format will be erroneous, such as circular routes where departures are presented as a time period with the route's headway time.
- Data is in English but can be set to Traditional and Simplified Chinese, see comments.

## Contributors

[pkboy](https://github.com/pkboy/)