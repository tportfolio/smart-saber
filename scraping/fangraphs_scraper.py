import collections
import csv
import os
import pandas as pd
import pickle
import time

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary


__author__ = 'Timothy'


"""batter_fg_list_scraper(browser, link=""):

Obtains list of batters from Fangraphs, filtering entries
based on plate appearances over the 2016 season.

Args:
    browser: An instantiation of the Selenium web browser.
    link: The Fangraphs link that should be scraped.

Pickles the player names with their respective links as tuples.

"""


def batter_fg_list_scraper(browser, link=""):
    if not link:
        link = "http://www.fangraphs.com/leaders.aspx?" \
               "pos=all&stats=bat&lg=all&qual=0&type=8&season=2016&month=0&season1=2016" \
               "&ind=0&team=0&rost=0&age=0&filter=&players=0&sort=4,d&page=1_352"

    browser.get(link)
    entries = browser.find_elements_by_xpath("/html/body/form/div[3]/div[2]/span[2]/div/table/tbody/tr")
    print(len(entries))

    batters = []
    for entry in entries:
        url = entry.find_element_by_tag_name("a")
        batters.append((url.text, url.get_attribute("href")))

        print(batters[-1])

    with open("batter_links_fg.data", "wb") as bl:
        pickle.dump(batters, bl)


"""batter_fg_csv_scraper(browser):

Manually creates CSVs of 2016 game logs for advanced statistics
of all players previously scraped in batter_fg_list_scraper.

Args:
    browser: An instantiation of the Selenium web browser.

Saves the game logs of each individual player as CSV files with the
naming convention "Firstname Lastname.csv".

"""


def batter_fg_csv_scraper(browser):
    bl = open("batter_links_fg.data", "rb")
    batters = pickle.load(bl)
    bl.close()
    os.chdir("../scraping/batting/fangraphs")

    for batter in batters:
        url = batter[1].replace("ss", "sd") + "&type=6&gds=&gde=&season=2016&sort=0,a"
        print(url)
        browser.get(url)

        tables = browser.find_elements_by_tag_name("tbody")
        table = tables[-1]
        games = table.find_elements_by_tag_name("tr")[1:]
        print(len(games))

        csv_info = []

        headers = ["Date", "Team", "Opp", "BO", "Pos", "FB%", "FBv", "SL%", "SLv", "CT%", "CTv", "CB%", "CBv",
                   "CH%", "CHv", "SF%", "SFv", "KN%", "KNv", "XX%"]
        print(",".join(headers))

        csv_info.append(headers)

        for game in games:
            stat_line = []
            cols = game.find_elements_by_tag_name("td")
            date = cols[0]
            rest = cols[1:]

            day = date.find_element_by_tag_name("a").text
            if day == "Date":
                print("header line")
                continue

            stat_line.append(day)

            for col in rest:
                val = col.text
                if val is " ":
                    val = 0
                elif "%" in val:
                    val = round(float(val.split(' ')[0]) / 100, 3)
                stat_line.append(str(val))

            csv_info.append(stat_line)

        for el in csv_info:
            print(el)

        with open(batter[0] + ".csv", "w") as fg:
            cw = csv.writer(fg, quoting=csv.QUOTE_NONE, lineterminator='\n')
            cw.writerows(csv_info)


"""fangraphs_batters_info(csv_name):

Obtains batting information of all players given a CSV file and stores it in OrderedDicts.

Args:
    csv_name: File name of the CSV to parse.

Pickles the information in OrderedDict form, which is later used to create DataFrames
with the Pandas module.

"""

def fangraphs_batters_info(csv_name):
    os.chdir("../scraping/batting/batter_profiles")
    bp = open("batter_profiles_updated.data", "rb")
    dicts = pickle.load(bp)
    bp.close()

    df = pd.read_csv(csv_name)
    suffix = csv_name.split('.')[0].rsplit(' ')[-1]
    print(suffix)
    df.columns = ['Season'] + list(df.columns[1:])
    print(df.columns)
    print(df)
    print(len(df.iloc[:]))

    headers = ['AVG', 'BB/K', 'OPS', 'GB/FB', 'LD%', 'Soft%', 'Med%', 'Hard%']
    for i in range(len(df.iloc[:])):
        batter = df.ix[i, "Name"]
        avg = round(df.ix[i, "AVG"], 3)
        bbk = round(df.ix[i, "BB/K"], 3)
        ops = round(df.ix[i, "OPS"], 3)
        gbfb = round(df.ix[i, "GB/FB"], 3)
        ld = df.ix[i, "LD%"]
        soft = df.ix[i, "Soft%"]
        med = df.ix[i, "Med%"]
        hard = df.ix[i, "Hard%"]

        vals = [batter, avg, bbk, ops, gbfb, ld, soft, med, hard]
        print(vals)
        curr_dict = dicts[batter]

        for i in range(len(vals[1:])):
            try:
                if "%" in vals[i+1]:
                    vals[i+1] = round(float(vals[i+1].split(' ')[0]) / 100, 3)
            except:
                pass

            curr_dict[headers[i] + " - " + suffix] = vals[i+1]
        print(curr_dict["Soft% - " + suffix])

    with open("batter_profiles_updated.data", "wb") as bl:
        pickle.dump(dicts, bl)