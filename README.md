# golf_scraper
Pulls historical data for pga tour, euro tour, web tour. Built on Scrapy.

### Disclaimer
1. Please don't use this maliciously, or overwhelm servers. Unaltered, it follows the websites' robots.txt files.
2. The PGA tour and Euro tour are fairly likely to update their websites over time and the way this is currently set up, it isn't very robust to change. I am likely to continue to use this in the future, and so I will try and maintain it. However, I can't guarantee that I will.

### Dependencies
* [scrapy](https://docs.scrapy.org/en/latest/)
* [scrapy_splash](https://github.com/scrapy-plugins/scrapy-splash)
* docker image to run scrapy_splash as detailed in the scrapy_splash docs

### Get Started

1. Set up scrapy_splash server. Typical command is ``` docker run -p 8050:8050 scrapinghub/splash ```

2. Run ``` scrapy crawl schedules ``` in the root directory to output a "sched.csv" file in the root directory. This will have all the tournament links for the years set in golf_scraper/settings.py.

3. Run ``` python3 insp.py  ``` to see if any years were missed (this is pretty common). Usually it takes 2-3 runs to get every year. Schedules.py should automatically detect if a year/tour's schedule has been picked up.

* Note: The Web tour doesn't go very far back, I start in 2010
* Another note: I also uploaded a copy of what the sched.py should output since the .csv file isn't that big. If you're lazy and it's still 2019 you can use that

4. 


<!--  -->
