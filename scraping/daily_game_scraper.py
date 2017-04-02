import collections
import csv
import os
import mlbgame
import pandas as pd
import pickle
import time

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

__author__ = 'Timothy'


def get_lineups(headless=1, verbose=1):

    all_batters = []
    all_pitchers = []

    if verbose:
        print("Loading browser...")

    if headless:
        browser = webdriver.PhantomJS(executable_path=r"C:\Users\Timothy\AppData\Roaming\npm\node_modules\phantomjs-prebuilt\lib\phantom\bin\phantomjs.exe")
    else:
        binary = FirefoxBinary(r'C:\Program Files\Mozilla Firefox 46\firefox.exe')
        fp = webdriver.FirefoxProfile(r'C:\Users\Timothy\AppData\Roaming\Mozilla\Firefox\Profiles\d9ra2s92.selenium')
        browser = webdriver.Firefox(firefox_binary=binary, firefox_profile=fp)

    if verbose:
        print("Connecting to FantasyLabs for current day's line-ups...")
    browser.get("http://www.fantasylabs.com/mlb/lineups/?date=04022017")
    time.sleep(1)

    if verbose:
        print("Scraping line-ups from FantasyLabs...")
    game_list = browser.find_elements_by_class_name("panel-primary")

    for game in game_list:
        projected_pitchers = game.find_elements_by_class_name("lineup-header")[1].find_elements_by_class_name("player-detail")
        for p in projected_pitchers:
            all_pitchers.append(p.text.split(" (")[0])

        if verbose:
            print("--------\nPitchers for this game:")
            print(all_pitchers[-2] + " (Away)")
            print(all_pitchers[-1] + " (Home)")

        projected_lineups = game.find_element_by_class_name("panel-body").find_elements_by_tag_name("ul")
        batters_away = projected_lineups[0].find_elements_by_tag_name("li")
        for b in batters_away:
            all_batters.append(b.find_element_by_tag_name("span").text)

        if verbose:
            print("\nAway Batting Lineup:")
            for i in range(len(batters_away)):
                print(str(i+1) + ". " + all_batters[(i-9)])

        batters_home = projected_lineups[1].find_elements_by_tag_name("li")
        for b in batters_home:
            all_batters.append(b.find_element_by_tag_name("span").text)

        if verbose:
            print("\nHome Batting Lineup:")
            for i in range(len(batters_home)):
                print(str(i+1) + ". " + all_batters[i-9])

    return all_pitchers, all_batters
