import collections
import csv
import os
import mlbgame
import pandas as pd
import pickle
import random
import time

from io import StringIO
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

__author__ = 'Timothy'


def mate_teams(batters, pitchers, lineups):
    outfielders = batters[-1]
    infielders = batters[:-1]

    new_lineup_list = lineups

    for i in range(len(lineups)):
        for j in range(i+1, len(lineups)):
            new_lineup = []
            salary_sum = 0
            for k in range(len(infielders)):
                rand_num = random.randint(0, 2)
                if rand_num == 2:
                    player_to_add = tuple_maker(infielders[k].iloc[random.randint(0, len(infielders[k].index)-1)])
                elif rand_num == 1:
                    player_to_add = lineups[i][k]
                else:
                    player_to_add = lineups[j][k]
                new_lineup.append(player_to_add)
                salary_sum += player_to_add[1]
            for l in range(3):
                rand_num = random.randint(0, 2)
                if rand_num == 2:
                    player_to_add = tuple_maker(outfielders.iloc[random.randint(0, len(outfielders.index)-1)])
                elif rand_num == 1:
                    player_to_add = lineups[i][len(infielders) + l]
                else:
                    player_to_add = lineups[j][len(infielders) + l]
                new_lineup.append(player_to_add)
                salary_sum += player_to_add[1]

            for m in range(2):
                rand_num = random.randint(0, 2)
                if rand_num == 2:
                    player_to_add = tuple_maker(pitchers.iloc[random.randint(0, len(pitchers.index)-1)])
                elif rand_num == 1:
                    player_to_add = lineups[i][len(infielders) + 3 + m]
                else:
                    player_to_add = lineups[j][len(infielders) + 3 + m]
                new_lineup.append(player_to_add)
                salary_sum += player_to_add[1]

            if len(new_lineup) != len(set(new_lineup)):
                print(new_lineup)
                print("Duplicate player found...")
                if lineups[i] not in new_lineup_list:
                    new_lineup_list.append(lineups[i])
            elif salary_sum > 50000:
                print(salary_sum)
                if lineups[j] not in new_lineup_list:
                    new_lineup_list.append(lineups[j])
            else:
                new_lineup_list.append(new_lineup)
    return new_lineup_list


def tuple_maker(player):
    name = player.name
    salary = player.Salary
    points = player.RGPoints
    return (name, salary, points)


def multiple_team_generator(batters, pitchers, num_teams):
    lineups = []

    for i in range(num_teams):
        lineup = random_team_generator(batters, pitchers)
        lineups.append(lineup)

    return lineups


def biological_lineup_selection():
    batter_dfs, pitcher_df = get_rg_predictions()

    # initialization
    lineups = multiple_team_generator(batter_dfs, pitcher_df, 10)
    lineups_sorted = sorted(lineups, key=lambda x: sum(y[2] for y in x), reverse=True)
    lineups_sorted = lineups_sorted[:3]
    for lineup in lineups_sorted:
        print(lineup)
        print(str(sum(player[2] for player in lineup)) + ' - ' + str(sum(player[1] for player in lineup)))
    # print(lineups)

    while True:
        new_teams = mate_teams(batter_dfs, pitcher_df, lineups_sorted)
        new_teams.extend(multiple_team_generator(batter_dfs, pitcher_df, 3))
        new_teams = sorted(new_teams, key=lambda x: sum(y[2] for y in x), reverse=True)[:3]
        print("new teams:")
        for team in new_teams:
            print(team)
            print(str(sum(player[2] for player in team)) + ' - ' + str(sum(player[1] for player in team)))
        if new_teams[0] == new_teams[1] and new_teams[1] == new_teams[2]:
            print("Final team:")
            print(new_teams[0])
            return new_teams[0]
        else:
            lineups_sorted = new_teams


def random_team_generator(batters, pitchers):
    outfielders = batters[-1]
    infielders = batters[:-1]

    while True:
        player_tuples = []
        salary_sum = 0

        for bdf in infielders:
            random_player = bdf.iloc[random.randint(0, len(bdf.index)-1)]
            player_tuple = tuple_maker(random_player)
            player_tuples.append(player_tuple)
            salary_sum += player_tuple[2]

        for i in range(3):
            random_player = outfielders.iloc[random.randint(0, len(outfielders.index)-1)]
            player_tuple = tuple_maker(random_player)
            player_tuples.append(player_tuple)
            salary_sum += player_tuple[2]

        for i in range(2):
            random_pitcher = pitchers.iloc[random.randint(0, len(pitchers.index)-1)]
            player_tuple = tuple_maker(random_pitcher)
            player_tuples.append(player_tuple)
            salary_sum += player_tuple[2]

        if len(player_tuples) != len(set(player_tuples)):
            print(player_tuples)
            print("Duplicate player found, restarting...")
        elif salary_sum > 50000:
            print(salary_sum)
            print("Too much money allocated, restarting...")
        else:
            return player_tuples


def split_batter_df(df):
    positions = ["C", "1B", "2B", "3B", "SS", "OF"]
    dfs_by_position = []
    for position in positions:
        dfs_by_position.append(df[df.Position.str.contains(position)])

    return dfs_by_position


def browser_initialization(headless):

    if headless:
        browser = webdriver.PhantomJS(executable_path=r"C:\Users\Timothy\AppData\Roaming\npm\node_modules\phantomjs-prebuilt\lib\phantom\bin\phantomjs.exe")
    else:
        binary = FirefoxBinary(r'C:\Program Files\Mozilla Firefox 46\firefox.exe')
        fp = webdriver.FirefoxProfile(r'C:\Users\Timothy\AppData\Roaming\Mozilla\Firefox\Profiles\d9ra2s92.selenium')
        browser = webdriver.Firefox(firefox_binary=binary, firefox_profile=fp)
    return browser

def get_rg_csv(browser, link):

    browser.get(link)
    csv_values = browser.find_element_by_tag_name("pre").text
    formatted_values = StringIO(csv_values)
    df = pd.read_csv(formatted_values, names=["Salary", "Team", "Position", "Opp", "Blank1", "Blank2", "RGPoints"])
    df = df.drop(["Blank1", "Blank2"], 1)

    return df


def get_rg_predictions(headless=1, verbose=1):

    if verbose:
        print("Loading browser...")

    browser = browser_initialization(headless)

    if verbose:
        print("Loading RotoGrinders batter projections...")
    batter_csv = get_rg_csv(browser, "https://rotogrinders.com/projected-stats/mlb-hitter.csv?site=draftkings")
    batter_dfs = split_batter_df(batter_csv)

    if verbose:
        print("Loading RotoGrinders pitcher projections...")
    pitcher_df = get_rg_csv(browser, "https://rotogrinders.com/projected-stats/mlb-pitcher.csv?site=draftkings")

    return batter_dfs, pitcher_df


def get_lineups(headless=1, verbose=1):

    all_batters = []
    all_pitchers = []

    if verbose:
        print("Loading browser...")

    browser = browser_initialization(headless)

    if verbose:
        print("Connecting to FantasyLabs for current day's line-ups...")
    browser.get("http://www.fantasylabs.com/mlb/lineups/?date=04042017")
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
