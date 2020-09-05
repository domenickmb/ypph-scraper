# ypph-scraper - Yellow Pages Philippines Scraper
### Description  
A menu driven program for extracting business information from [Yellow Pages Philippines](http://yellow-pages.ph). It uses the requests and beautifulsoup4 library to fetch and generate menu entries and then runs scrapy under the hood to crawl every link and scrape business details about the specific category you selected from the menu.

***

### Extracted data
The extacted data will be saved to a file (filename will be automatically generated based on the category name) and will be exported to a format based on the format you have selected from the menu. It supports the following formats:  
  * csv
  * json
  * json lines
  * xml

***

### Downloading and and running the program
You can download and extract the zip file from this repository or you can clone it if you have git installed on your system.
```bash
$ git clone https://github.com/domenickmb/ypph-scraper.git
```
Then `cd` to the ypph-scraper directory and install the necessary dependencies.
```bash
$ cd ypph-scraper
$ pip install -r requirements.txt
```
If all goes well you can now run the program by typing the following:
```bash
$ python ypph-scraper.py
```

***

### Screenshots
![image1](/images/image1.jpg)
![image2](/images/image2.jpg)
![image3](/images/image3.jpg)
![image4](/images/image4.jpg)
![image5](/images/image5.jpg)
