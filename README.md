# golf_scraper
Pulls historical data for pga tour, euro tour, web tour. Built on Scrapy. The Medium post this was built for can be found [here](https://medium.com/@BlakeAtkinson/rating-sports-teams-maximizing-a-generic-system-772144574a07?postPublishedType=initial).

### Disclaimer
1. Please don't use this maliciously, or overwhelm servers. Unaltered, it follows the websites' robots.txt files.
2. The PGA tour and Euro tour are fairly likely to update their websites over time and the way this is currently set up, it isn't very robust to change. I am likely to continue to use this in the future, and so I will try and maintain it. However, I can't guarantee that I will.

### Dependencies
* [scrapy](https://docs.scrapy.org/en/latest/)
* [scrapy_splash](https://github.com/scrapy-plugins/scrapy-splash)
* docker image to run scrapy_splash as detailed in the scrapy_splash docs
* I use tabula on some special case Euro tournaments

### Get Started

1. Set up scrapy_splash server. Typical command is ``` docker run -p 8050:8050 scrapinghub/splash ```

2. Run ``` scrapy crawl schedules ``` in the root directory to output a "sched.csv" file in the root directory. This will have all the tournament links for the years set in golf_scraper/settings.py.

3. Run ``` python3 insp.py  ``` to see if any years were missed (this is pretty common). Usually it takes 2-3 runs to get every year. The schedules bot should automatically detect if a year/tour's schedule has been picked up.

* Note: The Web tour doesn't go very far back, I start in 2010
* Another note: I also uploaded a copy of what the sched.py should output since the .csv file isn't that big. If you're lazy and it's still 2019 you can use that

4. Once the schedule is complete, it's time to collect leaderboards. ```scrapy crawl scores``` will iterate through the schedule and collect links. Through trial and error, there are many tournaments that are match play or cancelled which make them unsuitable for my ratings system. I skip them automatically. I usually only collect about 100 tournaments at a time because something usually goes wrong.

There are about 8 tournaments that Euro Tour only has special javascript leaderboards for. Instead of writing a completely new parse function just for those tournaments, I downloaded a .pdf of the results and parsed that.

Once a few tournaments are collected, I run ```python3 save.py```. This adds them to a "has saved" csv file so that they're not collected again. If there are collection errors, you don't have to run ```save.py``` and it won't record those tournaments. Tournaments are outputted to a leaderboards folder in the format leaderboard/[season]/[tour]/[tournament_name].csv.

The nature of this collection is rocky, and the websites (especially the PGA Tour website)  are not built with scrapers in mind. Therefore this repo will probably run into issues. Let me know if you have any, I'll try and diagnose.

<!-- end -->
