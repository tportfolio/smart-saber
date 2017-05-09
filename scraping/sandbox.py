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

from tkinter import *

import fangraphs_scraper as fs
import baseball_reference_scraper as brs
import dataframe_creation as dfc
import daily_game_scraper as dgs
import modeling as mdl

__author__ = 'Timothy'


num_lineups = 100
use_rfr = True

def main():
    #Tkinter window adapted from http://stackoverflow.com/a/17457435
    root = Tk()
    root.minsize(width=200, height=125)
    lineup_type = BooleanVar()
    lineup_type.set("True")
    desired_lineups = IntVar()

    label_nl = Label(root, text="Number of Lineups")
    entry_nl = Entry(root, bd=5, textvariable=desired_lineups)

    rfr = Radiobutton(root, text="Random Forest", variable=lineup_type, value=True)
    rg = Radiobutton(root, text="Rotogrinders", variable=lineup_type, value=False)

    def get_vars():
        global num_lineups
        global use_rfr
        num_lineups = int(entry_nl.get())
        use_rfr = lineup_type.get()
        print(num_lineups)
        print(use_rfr)
        root.destroy()

    send_vars = Button(root, text="Submit", command=get_vars)

    label_nl.pack()
    entry_nl.pack()
    rfr.pack()
    rg.pack()
    send_vars.pack(side=BOTTOM)
    root.mainloop()

    ########################

    lineups = []
    for i in range(num_lineups):
        lineups.append(dgs.biological_lineup_selection(rfr=use_rfr))
    lineups = sorted(lineups, key=lambda x: sum(y[2] for y in x), reverse=True)
    for lineup in lineups:
        print(lineup)
        print(str(sum(player[2] for player in lineup)) + ' - ' + str(sum(player[1] for player in lineup)))

    if use_rfr:
        os.chdir("best_rfr_lineups")
    else:
        os.chdir("best_rg_lineups")
    if not os.path.isdir(dgs.get_current_date()):
        os.mkdir(dgs.get_current_date())
    os.chdir(dgs.get_current_date())

    timestamp = str(int(time.time()))
    os.mkdir(timestamp)
    os.chdir(timestamp)
    with open("lineup.data", "wb") as lf:
        pickle.dump(lineups, lf)
    with open("lineup.txt", "w") as lf:
        for lineup in lineups:
            lf.write(str(lineup) + "\n")
            lf.write(str(sum(player[2] for player in lineup)) + ' - ' + str(sum(player[1] for player in lineup)) + "\n")
    os.chdir("../../..")


    # temp = open("daily_rfr_projections/04152017/batter_projections_04152017.data", "rb")
    # df = pickle.load(temp)
    # print(df[df.Position.str.contains("SS")])



    # pp = open("finalized_data_structures/pitcher_avg_splits_2016.dframe", "rb")
    # batters = pickle.load(pp)
    # pp.close()
    # print(batters)
    # print(batters)
    # print(batters.sum())
    # batters = batters.sum()
    # print(batters["AVG - Away"])


if __name__ == "__main__":
    main()