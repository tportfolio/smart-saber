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

import fangraphs_scraper as fs
import baseball_reference_scraper as brs
import dataframe_creation as dfc
import daily_game_scraper as dgs


__author__ = 'Timothy'


def main():

    # day = mlbgame.day(2017, 4, 2)
    # for game in day:
    #     print(game)
    #     stats = mlbgame.player_stats(game.game_id)
    #     print(stats['home_batting'])

    pdf = open("pitchers.dframe", "rb")
    df = pickle.load(pdf)
    pdf.close()

    bdf = open("batters.dframe", "rb")
    df2 = pickle.load(bdf)
    bdf.close()
    df2 = df2.dropna()

    pitchers, batters = dgs.get_lineups()
    print("-----\nPitchers for today:")
    for p in pitchers:
        print(p + " - " + str(p in list(df.index.values)))
    print("-----\nBatters for today:")
    for b in batters:
        print(b + " - " + str(b in list(df2.index.values)))

    print(len(pitchers))
    print(len(batters))

    # df = pd.read_csv("DraftKings Salaries.csv")
    # df = df[["Position", "Name", "Salary", "AvgPointsPerGame"]]
    # df = df[df.Position != "RP"]
    # print(df)
    #
    # df2 = pd.read_csv("RotoGrinders Template.csv")
    # print(df2)

    # salaries = df.Salary.tolist()
    # points = df.AvgPointsPerGame.tolist()
    # print(salaries)
    # print(points)

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


if __name__ == "__main__":
    main()