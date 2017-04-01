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


"""batter_gamelog_df_initialization():

Converts OrderedDicts to DataFrame objects for individual batter game logs.

Pickles the DataFrame for later augmentation.

"""


def batter_gamelog_df_initialization():
    os.chdir("../scraping")
    bl = open("batter_links_br.data", "rb")
    links = pickle.load(bl)
    bl.close()

    print(len(links))
    for link in links:
        print(link[0])
        with open("batting/fangraphs/" + link[0] + ".csv", "rb") as bp:
            df = pd.read_csv(bp)
            info = df[['Opp', 'BO']]
            info = info.assign(Home=0, Away=0)
            for i in range(len(info.index)):
                if "@" in info.ix[i, "Opp"]:
                    info.ix[i, "Away"] = 1
                else:
                    info.ix[i, "Home"] = 1
            del info["Opp"]
            print(info)
            with open("batting/batter_profiles/" + link[0] + ".dframe", "wb") as bdf:
                pickle.dump(info, bdf)


"""finalize_batter_game_log_dfs(browser):

Finalizes DataFrame objects for individual batter game logs with information from other
DataFrame objects.

Args:
    browser: An instantiation of the Selenium web browser.

Pickles the DataFrames for usage with the sklearn package and related modules.

"""


def finalize_batter_game_log_dfs(browser):
    bs = open("box_scores.dframe", "rb")
    box_scores = pickle.load(bs)
    bs.close()

    pd = open("pitchers.dframe", "rb")
    pitchers = pickle.load(pd)
    pd.close()

    bl = open("batter_links_br.data", "rb")
    links = pickle.load(bl)
    bl.close()

    bp = open("batters.dframe", "rb")
    batters = pickle.load(bp)
    bp.close()
    print(batters)

    headers = ["AVG", "OBP%", "SLG%", "SO/BB"]
    headers_ha = ["AVG_HA", "OBP_HA", "SLG_HA", "SOBB_HA"]
    headers_lr = ["AVG_LR", "OBP_LR", "SLG_LR", "SOBB_LR"]

    inconsistent_batter_logs = []
    print(os.listdir("./batting/batter_profiles"))

    for link in links:
        if not (link[0] + " updated.dframe" in os.listdir("./batting/batter_profiles")):
            print(link[0])
            if link[0] == "A.J. Pierzynski":
                browser.get("http://www.baseball-reference.com/players/gl.fcgi?id=pierza.01&t=b&year=2016")
            else:
                browser.get(link[1])

            game_list = browser.find_element_by_id("batting_gamelogs")
            games = game_list.find_elements_by_css_selector("[id^=batting_gamelogs]")
            print(len(games))
            # AVG, OBP%, SLG%, SO/BB
            with open("./batting/batter_profiles/" + link[0] + ".dframe", "rb") as dff:
                df = pickle.load(dff)

                if len(df.index) != len(games):
                    inconsistent_batter_logs.append(link[0])
                    continue

                df = df.assign(LHP=0, RHP=0)
                df = df.assign(AVG_HA=0, OBP_HA=0, SLG_HA=0, SOBB_HA=0,
                               AVG_LR=0, OBP_LR=0, SLG_LR=0, SOBB_LR=0)
                df = df.assign(Points=0)

                bats_overall = batters.ix[link[0], "Bats:"]
                print(bats_overall)

                count = 0
                for i in range(len(games)):
                    game_id = games[i].find_element_by_xpath("td[3]").find_element_by_tag_name("a").get_attribute(
                        "href")
                    game_id = game_id.split('/')[-1].strip(".shtml")
                    print(game_id)

                    box_score = box_scores.ix[game_id]
                    if df.ix[i, "Away"]:  # want opposing side
                        opp = box_score["Home"]
                    else:
                        opp = box_score["Away"]

                    pitcher = opp["Pitcher"]

                    if pitcher in pitchers.index.get_values():
                        # print(pitchers.ix[pitcher])
                        print(pitcher)
                        if pitchers.ix[pitcher, "Throws:"] == "Left":
                            df.ix[i, "LHP"] = 1
                        else:
                            df.ix[i, "RHP"] = 1
                        count += 1

                        bats = bats_overall
                        if bats == "Both":
                            bats = "Right" if df.ix[i, "LHP"] else "Left"

                        print(bats)

                        for j in range(len(headers)):
                            df.ix[i, headers_ha[j]] = pitchers.ix[pitcher, headers[j] + " - Home"] if df.ix[i, "Away"] \
                                else pitchers.ix[pitcher, headers[j] + " - Away"]
                            df.ix[i, headers_lr[j]] = pitchers.ix[pitcher, headers[j] + " - LHB"] if bats == "Left" \
                                else pitchers.ix[pitcher, headers[j] + " - RHB"]

                    points = games[i].find_element_by_xpath("td[35]").text
                    print(points)
                    df.ix[i, "Points"] = points
                print("Total relevant games = " + str(count))
                print(df)
                with open("./batting/batter_profiles/" + link[0] + " updated.dframe", "wb") as ndff:
                    pickle.dump(df, ndff)

    with open("inconsistencies.txt", "w") as inc:
        for el in inconsistent_batter_logs:
            inc.write(el + "\n")


"""pitcher_gamelog_df_initialization():

Converts OrderedDicts to DataFrame objects for individual batter game logs.

Pickles the DataFrame for later augmentation.

"""


def pitcher_gamelog_df_initialization():
    os.chdir("../scraping")
    bl = open("pitcher_links_br.data", "rb")
    links = pickle.load(bl)
    bl.close()

    print(len(links))
    for link in links:
        print(link[0])
        with open("pitching/baseball-reference/" + link[0] + ".csv", "rb") as bp:
            df = pd.read_csv(bp)
            df = df[:-1]
            # try:
            #     df = df[df['DR'].str.contains("Player")==True]  # remove trade notifications
            # except AttributeError:
            #     pass  # irrelevant for most cases

            df['Unnamed: 5'] = df['Unnamed: 5'].astype(str)
            df['DR'] = df['DR'].astype(int)
            print(df)

            info = df[['Unnamed: 5', 'DR']]
            info.DR[info.DR > 10] = 10  # remove extra outliers in days rest
            info = info.assign(Home=0, Away=0)

            for i in range(len(info.index)):
                if "@" in info.ix[i, "Unnamed: 5"]:
                    info.ix[i, "Away"] = 1
                else:
                    info.ix[i, "Home"] = 1
            del info["Unnamed: 5"]

            print(info)
            with open("pitching/pitcher_profiles/" + link[0] + ".dframe", "wb") as pdf:
                pickle.dump(info, pdf)


"""pitcher_gamelog_df_initialization():

Converts OrderedDicts to DataFrame objects for individual batter game logs.

Pickles the DataFrame for later augmentation.

"""

def finalize_pitcher_game_log_dfs(browser):
    bs = open("box_scores.dframe", "rb")
    box_scores = pickle.load(bs)
    bs.close()

    pd = open("pitchers.dframe", "rb")
    pitchers = pickle.load(pd)
    pd.close()

    bl = open("pitcher_links_br.data", "rb")
    links = pickle.load(bl)
    bl.close()

    bp = open("batters.dframe", "rb")
    batters = pickle.load(bp)
    bp.close()
    batters = batters.dropna()
    print(batters)

    headers = ["AVG", "BB/K", "GB/FB", "OPS"]
    headers_ha = ["AVG_HA", "BB_K_HA", "GB_FB_HA", "OPS_HA"]
    headers_lr = ["AVG_LR", "BB_K_LR", "GB_FB_LR", "OPS_LR"]

    inconsistent_pitcher_logs = []
    print(os.listdir("./pitching/pitcher_profiles"))

    for link in links:
        if not (link[0] + " updated.dframe" in os.listdir("./pitching/pitcher_profiles")):
            print(link[0])
            if link[0] == "CC Sabathia":
                browser.get("http://www.baseball-reference.com/players/gl.fcgi?id=sabatc.01&t=p&year=2016")

            else:
                browser.get(link[1])

            game_list = browser.find_element_by_id("pitching_gamelogs")
            games = game_list.find_elements_by_css_selector("[id^=pitching_gamelogs]")
            print(len(games))

            with open("./pitching/pitcher_profiles/" + link[0] + ".dframe", "rb") as dff:
                df = pickle.load(dff)

                if len(df.index) != len(games):
                    inconsistent_pitcher_logs.append(link[0])
                    continue

                # df = df.assign(Left_Batters=0, Right_Batters=0, Switch_Batters=0)
                df = df.assign(AVG_HA=0, BB_K_HA=0, GB_FB_HA=0, OPS_HA=0,
                               AVG_LR=0, BB_K_LR=0, GB_FB_LR=0, OPS_LR=0)
                df = df.assign(Points_Last5=0)
                df = df.assign(Points=0)

                throws = pitchers.ix[link[0], "Throws:"]

                for i in range(len(games)):
                    game_id = games[i].find_element_by_xpath("td[3]").find_element_by_tag_name("a").get_attribute(
                        "href")
                    game_id = game_id.split('/')[-1].strip(".shtml")
                    print(game_id)

                    box_score = box_scores.ix[game_id]
                    if df.ix[i, "Away"]:  # want opposing side
                        opp = box_score["Home"]
                    else:
                        opp = box_score["Away"]

                    lineup = opp["Batters"]

                    batter_count = 0
                    for batter in lineup:
                        if batter in batters.index.get_values():
                            batter_count += 1
                            # print(pitchers.ix[pitcher])
                            print(batter)
                            # bats = batters.ix[batter, "Bats:"]

                            # if bats == "Left":
                            #     df.ix[i, "Left_Batters"] += 1
                            # elif bats == "Right":
                            #     df.ix[i, "Right_Batters"] += 1
                            # else:  # Both
                            #     df.ix[i, "Switch_Batters"] += 1

                            for j in range(len(headers)):
                                if df.ix[i, "Away"]:
                                    df.ix[i, headers_ha[j]] += batters.ix[batter, headers[j] + " - Home"]
                                else:
                                    df.ix[i, headers_ha[j]] += batters.ix[batter, headers[j] + " - Away"]

                                if throws == "Left":
                                    df.ix[i, headers_lr[j]] += batters.ix[batter, headers[j] + " - LHP"]
                                else:
                                    df.ix[i, headers_lr[j]] += batters.ix[batter, headers[j] + " - RHP"]

                            # print(df.ix[i, "Left_Batters"])
                            # print(df.ix[i, "Right_Batters"])
                            # print(df.ix[i, "Switch_Batters"])

                    # total_batters = df.ix[i, "Left_Batters"] + df.ix[i, "Right_Batters"] + df.ix[i, "Switch_Batters"]

                    for el in headers_ha:
                        df.ix[i, el] /= batter_count
                    for el in headers_lr:
                        df.ix[i, el] /= batter_count

                    points = games[i].find_element_by_xpath("td[46]").text
                    print(points)
                    df.ix[i, "Points"] = float(points)

                    if 0 < i < 5:
                        summed_df = df.loc[0:i-1, ["Points"]].sum()
                        df.ix[i, "Points_Last5"] = summed_df["Points"] / i
                    elif i > 0:
                        summed_df = df.loc[i-5:i-1, ["Points"]].sum()
                        df.ix[i, "Points_Last5"] = summed_df["Points"] / 5

                summed_df = df.loc[0:len(df.index), ["Points"]].sum()
                df.ix[0, "Points_Last5"] = summed_df["Points"] / len(df.index)

                print(df)
                with open("./pitching/pitcher_profiles/" + link[0] + " updated.dframe", "wb") as ndff:
                    pickle.dump(df, ndff)

    with open("inconsistencies_p.txt", "w") as inc:
        for el in inconsistent_pitcher_logs:
            inc.write(el + "\n")

"""pitching_profiles_to_df():

Converts OrderedDicts to DataFrame objects for pitcher season split profiles.

Pickles the DataFrame for later usage.

"""


def pitching_profiles_to_df():
    os.chdir("../scraping/pitching/pitcher_profiles")
    pp = open("pitcher_profiles_updated.data", "rb")
    pitcher_profiles = pickle.load(pp)
    pp.close()

    df = pd.DataFrame.from_dict(pitcher_profiles).transpose()
    print(df)

    with open("pitchers.dframe", "wb") as pdf:
        pickle.dump(df, pdf)


"""batting_profiles_to_df():

Converts OrderedDicts to DataFrame objects for batter season split profiles.

Pickles the DataFrame for later usage.

"""


def batting_profiles_to_df():
    pp = open("batter_profiles_updated.data", "rb")
    batter_profiles = pickle.load(pp)
    pp.close()

    df = pd.DataFrame.from_dict(batter_profiles).transpose()
    print(df)

    # pp = open("batter_profiles.data", "rb")
    # batter_profiles = pickle.load(pp)
    # pp.close()
    # df2 = pd.DataFrame.from_dict(batter_profiles).transpose()
    # print(df2)
    #
    # final_df = pd.concat([df, df2], axis=1, join_axes=[df.index])
    # print(final_df)

    with open("batters.dframe", "wb") as pdf:
        pickle.dump(df, pdf)


"""bbox_scores_to_df():

Converts OrderedDicts to DataFrame objects for box scores of all games.

Pickles the DataFrame for later usage.

"""


def box_scores_to_df():
    bs = open("box_scores_dicts.data", "rb")
    batter_profiles = pickle.load(bs)
    bs.close()
    df = pd.DataFrame.from_dict(batter_profiles).transpose()
    print(df)
    with open("box_scores.dframe", "wb") as bsdf:
        pickle.dump(df, bsdf)


def testing(browser):
    browser.get("http:/www.reddit.com")