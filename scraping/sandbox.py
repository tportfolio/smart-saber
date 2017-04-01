import collections
import csv
import os
import pandas as pd
import pickle
import time

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

import fangraphs_scraper as fs
import baseball_reference_scraper as brs
import dataframe_creation as dfc


__author__ = 'Timothy'


def main():


    #
    # print(pitcher_profiles.head())
    # print(pitcher_profiles.ix["Tim Adleman"])
    #
    # with open("./batting/batter_profiles/Christian Bethancourt.dframe", "rb") as dff:
    #     df = pickle.load(dff)
    #     print(df)
    #
    binary = FirefoxBinary(r'C:\Program Files\Mozilla Firefox 46\firefox.exe')
    fp = webdriver.FirefoxProfile(r'C:\Users\Timothy\AppData\Roaming\Mozilla\Firefox\Profiles\d9ra2s92.selenium')
    browser = webdriver.Firefox(firefox_binary=binary, firefox_profile=fp)
    dfc.finalize_pitcher_game_log_dfs(browser)
    # dfc.testing(browser)
    #
    # pp = open("batters.dframe", "rb")
    # batters = pickle.load(pp)
    # pp.close()
    # batters = batters.loc[["Jose Altuve", "Nolan Arenado"], ["AVG - Away"]]
    # print(batters)
    # print(batters.sum())
    # batters = batters.sum()
    # print(batters["AVG - Away"])



    # os.chdir("../scraping/batting/batter_profiles")
    # bl = open("Jose Abreu.dframe", "rb")
    # abreu = pickle.load(bl)
    # bl.close()
    #
    # print(abreu)

    # with open("box_scores_dicts.data", "rb") as bs:
    #     temp = pickle.load(bs)
    #     game = temp["CLE201608190"]
    #     away = game["Away"]
    #     home = game["Home"]
    #
    #     print(away["Batters"])
    #     print(home["Pitcher"])

    # pl = open("pitcher_profiles.data", "rb")
    # pitchers = pickle.load(pl)
    # pl.close()
    #
    # noah = pitchers["Madison Bumgarner"]
    # for key in noah.keys():
    #     print(key + " - " + noah[key])

    # fangraphs_batters_info("FanGraphs Splits Leaderboard Data -- vs LHP.csv")
    # fangraphs_batters_info("FanGraphs Splits Leaderboard Data -- vs RHP.csv")
    # fangraphs_batters_info("FanGraphs Splits Leaderboard Data -- Home.csv")
    # fangraphs_batters_info("FanGraphs Splits Leaderboard Data -- Away.csv")

    # os.chdir("../scraping/pitching/pitcher_profiles")
    # bp = open("pitcher_profiles_updated.data", "rb")
    # dicts = pickle.load(bp)
    # bp.close()
    #
    # noah = dicts["Noah Syndergaard"]
    # for key in noah.keys():
    #     print(key + " - " + str(noah[key]))


if __name__ == "__main__":
    main()