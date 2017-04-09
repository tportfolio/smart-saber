import collections
import csv
import datetime
import glob
import os
import mlbgame
import pandas as pd
import pickle
import random
import time

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

import fangraphs_scraper as fs
import baseball_reference_scraper as brs
import dataframe_creation as dfc
import daily_game_scraper as dgs
import modeling as mdl


__author__ = 'Timothy'


def main():
    # dgs.biological_lineup_selection()

    # pdf = open("finalized_data_structures/pitcher_avg_splits_2016.dframe", "rb")
    # df = pickle.load(pdf)
    # pdf.close()
    # print(df)
    #
    # bdf = open("finalized_data_structures/batter_avg_splits_2016.dframe", "rb")
    # df2 = pickle.load(bdf)
    # bdf.close()
    # df2 = df2.dropna()
    # print(df2)

    pitchers, batters = dgs.get_lineups(return_tuples=True)
    print("-----\nPitchers for today:")
    for p in pitchers:
        # print(p + " - " + str(p in list(df.index.values)))
        print(p)
    print("-----\nBatters for today:")
    for b in batters:
        # print(b + " - " + str(b in list(df2.index.values)))
        print(b)

    # batters, pitchers = dgs.get_predictions(rfr=True)
    # print(batters)
    # print(pitchers)

    # print(len(pitchers))
    # print(len(batters))

    # lineup = dgs.random_team_generator(batter_dfs, pitcher_df)
    # print(lineup)
    # print(sum(x[1] for x in lineup))
    # print(sum(x[2] for x in lineup))

    # pp = open("batters.dframe", "rb")
    # batters = pickle.load(pp)
    # pp.close()

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