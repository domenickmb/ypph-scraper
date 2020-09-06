#!/usr/bin/python
#
# Author: Domenick M. Botardo
#
# Program Description:
#   Menu driven program to scrapde business details on
#   Yellow Pages Philippines (http://yellow-pages.ph)

import subprocess
import sys
import requests
import scrapy
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup

class Category:
    def __init__(self, name, href):
        self.name = name
        self.href = href
        
    def get_category(self):
        return self.href.split('/')[-2]

    def build_filename(self, ext):
        return self.href.split('/')[-2] + ext
      

class YellowpagesItem(scrapy.Item):
    business_name = scrapy.Field()
    address = scrapy.Field()
    landline = scrapy.Field()
    mobile = scrapy.Field()
    email = scrapy.Field()
    website = scrapy.Field()
    rating = scrapy.Field()
    reviews = scrapy.Field()


class YellowpagesSpider(scrapy.Spider):
    name = 'yellowpages'
    custom_settings = {
        'USER_AGENT': 'Googlebot',
        'ROBOTSTXT_OBEY': True,
        'DOWNLOAD_DELAY': 1.8,
        'LOG_FILE': 'debug.log',
    }

    def start_requests(self):
        url = 'http://yellow-pages.ph'
        yield scrapy.Request('/'.join([url, 'category', self.category, 'page-1']))

    def parse(self, response):
        # get all business links
        internal_links = response.css('.search-tradename a::attr(href)').getall()

        # follow all business links and extract details
        yield from response.follow_all(internal_links, callback=self.parse_details)

        # follow all pagination links
        pagination_links = response.css('ul.pagination a::attr(href)').re(r'^/category/.*')
        yield from response.follow_all(pagination_links, self.parse)

    def parse_details(self, response):
        # Skip if not on the business page
        if not response.url.startswith('https://www.yellow-pages.ph/business'):
            return None

        business_name = response.css('.header-name-container h1::text').get().strip()
        address = response.css('div.icon-name a.biz-link::text').get().strip()
        landline = response.css('.more-landline-container span.phn-txt::text').getall()
        mobile = response.css('.more-mobile-container span.phn-txt::text').getall()
        email = [s.strip() for s in response.css('a.email-link::text').getall()]
        website = [s.strip() for s in response.css('a.website-link::attr(href)').getall()]
        try:
            business_rating = response.css('.business-rating div.mr-1::text').re(r'\d\.\d')[0]
        except IndexError:
            business_rating = 'No rating'
        try:
            reviews = response.css('.search-star-number::text').re(r'\d+')[0]
        except IndexError:
            reviews = 'No reviews'

        # Populate items
        item = YellowpagesItem()
        item['business_name'] = business_name
        item['address'] = address
        item['landline'] = landline
        item['mobile'] = mobile
        item['email'] = email
        item['website'] = website
        item['rating'] = business_rating
        item['reviews'] = reviews
        yield item


def display_banner():
    subprocess.call(['clear'])
    print("o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o")
    print("|                       _                                                 |")
    print("|     _   _ _ __  _ __ | |__        ___  ___ _ __ __ _ _ __   ___ _ __    |")
    print("|    | | | | '_ \| '_ \| '_ \ _____/ __|/ __| '__/ _` | '_ \ / _ \ '__|   |")
    print("|    | |_| | |_) | |_) | | | |_____\__ \ (__| | | (_| | |_) |  __/ |      |")
    print("|     \__, | .__/| .__/|_| |_|     |___/\___|_|  \__,_| .__/ \___|_|      |")
    print("|     |___/|_|   |_|                                  |_|                 |")
    print("|                    Yellow Pages Philippines Scraper                     |")
    print("|                           (yellow-pages.ph)                             |")
    print("o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o")


def abort_program():
    print("[!] Program Aborted")
    sys.exit()


def display_menu(prompt, category_list):
    print(prompt)
    for index, value in enumerate(category_list, start=1):
        if isinstance(value, Category):
            value = value.name
        print(f"[{index}] {value}")


def get_selection(prompt, category_list):
    while True:
        display_menu(prompt, category_list)
        selection = get_userinput('Your choice[-1 to abort]: ', category_list)
        if selection:
            break
        else:
            print_error("[-] Invalid choice!")
    subprocess.call(['clear'])
    return selection


def safe_input(prompt):
    try:
        selection = input(prompt)
    except EOFError:
        print()
        abort_program()
    except KeyboardInterrupt:
        print()
        abort_program()
    return selection


def get_userinput(prompt, categories):
    selection = safe_input(prompt)
    try:
        selection = int(selection)
    except ValueError:
        return None
    if selection == -1:
        abort_program()
    elif selection not in range(1, len(categories)+1):
        return None
    return categories[selection - 1]


def get_data_format():
    data_format = [
        ('CSV', '.csv'),
        ('JSON', '.json'),
        ('JSON Lines', '.jl'),
        ('XML', '.xml'),
    ] 
    while True:
        print("Please select the data format for saving the output")
        for elem, (name, ext) in enumerate(data_format, start=1):
            print(f"[{elem}] ({ext}) {name}")
        choice = safe_input("Your choice[-1 to abort]: ")
        try:
            choice = int(choice)
        except ValueError:
            print_error("[-] Invalid input")
            continue
        if choice == -1:
            abort_program()
        choice -= 1
        if choice not in range(len(data_format)):
            print_error("[-] Invalid input!")
        else:
            break
    return data_format[choice][1]
            

def print_error(msg):
    print('[-] Invalid input!')
    subprocess.call(['sleep', '1'])
    subprocess.call(['clear'])


def runscrapy(selection, filename):
    print(f"[+] Extracted data will be saved to: '{filename}'")
    subprocess.call(['sleep', '1'])
    print(f"[+] Scraping business details under '{selection.name}' category...")
    subprocess.call(['sleep', '1'])
    category = selection.get_category()
    feed_format = filename.split('.')[-1]
    YellowpagesSpider.category = category
    YellowpagesSpider.custom_settings['FEED_URI'] = filename
    YellowpagesSpider.custom_settings['FEED_FORMAT'] = feed_format
    process = CrawlerProcess()
    process.crawl(YellowpagesSpider)
    process.start()
    print(f"Extracted data saved to: '{filename}'")


def main():
    categories = []
    subcategories = {}
    # send a get request to yellow-pages.ph/category
    page = requests.get('https://yellow-pages.ph/category')
    # get the page soup
    soup = BeautifulSoup(page.text, 'html.parser')
    # populate categories and subcategories
    for s in soup.find_all('div', {'class':'mt-3'}):
        # get category name
        category_name = s.find('h4', {'class':'category-h4'}).text.strip()
        categories.append(category_name)
        subcategory = []
        # get all subcategories under of that category
        for item in s.find_all('a', {'class':'category-item'}):
            name = item.find('span').text.strip()
            href = item.attrs['href']
            subcategory.append(Category(name, href))
        subcategories[category_name] = subcategory

    display_banner()
    main_category = get_selection("Please select from the general categories", categories)
    print('[*]', main_category)
    print('-' * 50)
    subcategory_list = subcategories[main_category]
    selection = get_selection("Please select a subcategory", subcategory_list)
    ext = get_data_format()
    filename = selection.build_filename(ext)
    subprocess.call(['sleep', '1'])
    runscrapy(selection, filename)


main()
