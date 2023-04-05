# Zumper Scraper

## Description

The Zumper Scraper is a Python script that scrapes the Zumper website for rental listings. The script will scrape all the listings for a given Provinces and save them to a CSV file.
To find the URL for a given province, see the Notes on Sitemap below.

## Usage

### Requirements

- Python 3.6+
- Scrapy==2.8.0

### Installation

1. Clone the repository
2. Install the requirements

```bash
pip install -r requirements.txt
```

### Running the script

```bash
scrapy crawl zumper  -o output.csv
```

Here the -o flag is used to specify the output file. The output file will be a CSV file.

## Notes

1. Sitemap(find urls for each province/state here): https://www.zumper.com/country/
2. Input file: input.txt
   Put the urls of the provinces/states you want to scrape in this file. Each url should be on a new line.
3. Proxy: It is recommended to use a proxy when scraping the Zumper website. To use a proxy, uncomment the following lines in the settings.py file:

```python
# PROXY = 'http://user:pass@ip:port'
```

Here, replace user, pass, ip and port with the appropriate values. Recommended proxy service: https://packetstream.io/
They rotate the IP addresses for you and you can use the same username and password for all the IP addresses.

Finally, uncomment the following lines in the zumper.py file:

```python
# 'proxy': self.settings.get('PROXY')
```

4. To update selectors for address(in case you encounter new formats for addresses), update the following lines in the zumper.py file:

```python
 ###### UPDATE THE LIST OF ADDRESS SELECTORS HERE ######
address_selectors = [
   'selector1',
   'selector2',
]

```

These are supposed to be xpath selectors.
