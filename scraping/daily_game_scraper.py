import collections
import datetime
import glob
import os
import pandas as pd
import pickle
import random
import time

from io import StringIO
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from sklearn.externals import joblib

__author__ = 'Timothy'


"""browser_initialization(headless):

Starts up a browser (either Firefox or PhantomJS browser, depending on input argument).

Args:
    headless: True indicates PhantomJS browser, False indicates visible Firefox browser.

Returns instantiation of the desired browser.

"""


def browser_initialization(headless):

    if headless:
        browser = webdriver.PhantomJS(executable_path=r"C:\Users\Timothy\AppData\Roaming\npm\node_modules\phantomjs-prebuilt\lib\phantom\bin\phantomjs.exe")
    else:
        binary = FirefoxBinary(r'C:\Program Files\Mozilla Firefox 46\firefox.exe')
        fp = webdriver.FirefoxProfile(r'C:\Users\Timothy\AppData\Roaming\Mozilla\Firefox\Profiles\d9ra2s92.selenium')
        browser = webdriver.Firefox(firefox_binary=binary, firefox_profile=fp)
    return browser


"""tuple_maker(player):

Creates a tuple of the player, given a DataFrame input.

Args:
    player: A DataFrame input with properties of the player relative to the game day.

Returns tuple of the player's name, DraftKings salary, and projected points.

"""


def tuple_maker(player):
    name = player.name
    salary = player.Salary
    points = player.Points
    return (name, salary, points)


"""mate_teams(batters, pitchers, lineups):

Randomly creates a new team from two input teams.

Args:
    batters: A DataFrame of all valid players.
    pitchers: A DataFrame of all valid pitchers.
    lineups: The two "parent" lineups to be "mated".

Returns new set of lineups after randomization.

"""


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


"""multiple_team_generator(batters, pitchers, num_teams):

Generates desired number of random teams.

Args:
    batters: A DataFrame of all valid players.
    pitchers: A DataFrame of all valid pitchers.
    num_teams: The number of teams to be created.

Returns desired cardinality of randomized lineups.

"""


def multiple_team_generator(batters, pitchers, num_teams):
    lineups = []

    for i in range(num_teams):
        lineup = random_team_generator(batters, pitchers)
        lineups.append(lineup)

    return lineups


"""biological_lineup_selection():

Generates the best lineup in a given randomized run with a genetic optimization algorithm.

Returns a list of tuples with the optimal players within..

"""


def biological_lineup_selection(rfr=False):
    batter_df, pitcher_df = get_predictions(rfr)
    batter_dfs = split_batter_df(batter_df)

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


"""random_team_generator(batters, pitchers):

Generates a random team within the constraints of a DraftKings lineup (positional and salary requirements).

Args:
    batters: A DataFrame of all valid players.
    pitchers: A DataFrame of all valid pitchers.

Returns a valid random lineup.

"""


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
            print("Money allocation is invalid, restarting...")
        else:
            return player_tuples


"""split_batter_df(df):

Splits batter DataFrame into distinct DataFrames based on positional eligibility.

Args:
    df: The batter DataFrame.

Returns a list of DataFrames, each of which only contains players at a particular position (e.g., catcher).

"""


def split_batter_df(df):
    positions = ["C", "1B", "2B", "3B", "SS", "OF"]
    dfs_by_position = []
    for position in positions:
        dfs_by_position.append(df[df.Position.str.contains(position)])

    return dfs_by_position


"""get_rg_df(browser, link):

Obtains CSV from RotoGrinders with adjusted formatting for DataFrame usage.

Args:
    browser: An instantiation of the Selenium-based browser.
    link: The link to the CSV.

Returns a properly formatted DataFrame of player information (DraftKings salaries, positional eligibility, etc.).

"""


def get_rg_df(browser, link):

    browser.get(link)
    csv_values = browser.find_element_by_tag_name("pre").text
    formatted_values = StringIO(csv_values)
    df = pd.read_csv(formatted_values, names=["Salary", "Team", "Position", "Opp", "Blank1", "Blank2", "Points"])
    df = df.drop(["Blank1", "Blank2"], 1)
    df = df[df.Salary != 0]

    return df


"""get_predictions(rfr=False, headless=True, verbose=True):

Scrapes RotoGrinders for predictions on current day's performances and creates DataFrames to hold information locally.

Args:
    rfr: True indicates adding random forest regression projections to DataFrames, False indicates skipping this tep.
    headless: True indicates PhantomJS browser, False indicates visible Firefox browser.
    verbose: True indicates printing all messages as the function operates, False indicates silent operation.

Returns two properly formatted DataFrames of player information (DraftKings salaries, positional eligibility, etc.),
    one for batters and one for pitchers.

"""


def get_predictions(rfr=False, headless=True, verbose=True):

    if rfr:
        os.chdir("daily_rfr_projections")
    else:
        os.chdir("daily_rg_projections")
    formatted_date = get_current_date()

    # we already have the desired projections
    if os.path.isdir(formatted_date):
        if verbose:
            print("Projections already downloaded, loading from pickled data.")
        os.chdir(formatted_date)

        with open("batter_projections_" + formatted_date + ".data", "rb") as dli:
            batter_df = pickle.load(dli)

        with open("pitcher_projections_" + formatted_date + ".data", "rb") as dli:
            pitcher_df = pickle.load(dli)

        os.chdir("../..")  # leave date, then projection folder

        return batter_df, pitcher_df

    # we need to fetch information from RotoGrinders
    if verbose:
        print("Loading browser...")

    browser = browser_initialization(headless)

    if verbose:
        print("Loading RotoGrinders batter projections...")
    batter_df = get_rg_df(browser, "https://rotogrinders.com/projected-stats/mlb-hitter.csv?site=draftkings")

    if verbose:
        print("Loading RotoGrinders pitcher projections...")
    pitcher_df = get_rg_df(browser, "https://rotogrinders.com/projected-stats/mlb-pitcher.csv?site=draftkings")

    os.mkdir(formatted_date)
    os.chdir(formatted_date)

    with open("batter_projections_" + formatted_date + ".data", "wb") as dli:
        pickle.dump(batter_df, dli)

    with open("pitcher_projections_" + formatted_date + ".data", "wb") as dli:
        pickle.dump(pitcher_df, dli)

    os.chdir("../..")

    if rfr:
        pitcher_tuples, batter_tuples = get_lineups(return_tuples=True)

        os.chdir("models/pitchers")
        pitcher_models = glob.glob("*.mdl")
        # for p in pitcher_models:
        #     print(p)
        os.chdir("../batters")
        batter_models = glob.glob("*.mdl")
        # for b in batter_models:
        #     print(b)
        os.chdir("../..")

        active_batters = [str(el) for el in list(batter_df.index.values)]
        active_pitchers = [str(el) for el in list(pitcher_df.index.values)]

        pdf = open("finalized_data_structures/pitcher_avg_splits_2016.dframe", "rb")
        pitcher_splits = pickle.load(pdf)
        pdf.close()
        print(pitcher_splits)

        bdf = open("finalized_data_structures/batter_avg_splits_2016.dframe", "rb")
        batter_splits = pickle.load(bdf)
        bdf.close()
        batter_splits = batter_splits.dropna()
        print(batter_splits)

        for batter in active_batters:
            if batter + ".mdl" not in batter_models or batter not in list(batter_splits.index.values):  # skip, default to original value
                continue

            else:
                current_tuple = ""
                for bt in batter_tuples:
                    if batter == bt[0]:  # name match
                        current_tuple = bt
                        break

                if not current_tuple:  # no gameday info, skip
                    continue

                else:  # we found a tuple, extract information
                    print(batter)
                    print(current_tuple)  # sample tuple: ('Dexter Fowler', 1, 'Away', 'Tanner Roark')
                    opp_pitcher = current_tuple[3]

                    if opp_pitcher in list(pitcher_splits.index.values):
                        # BO | Away | Home | LHP | RHP | AVG_HA | AVG_LR | OBP_HA | OBP_LR | SLG_HA | SLG_LR | SOBB_HA | SOBB_LR
                        bats_overall = batter_splits.ix[batter, "Bats:"]
                        prediction_input = [current_tuple[1]]  # BO

                        if current_tuple[2] == "Away":
                            prediction_input.extend([1, 0])  # Away=1, Home=0
                        else:
                            prediction_input.extend([0, 1])  # Away=0, Home=1

                        if pitcher_splits.ix[opp_pitcher, "Throws:"] == "Left":
                            prediction_input.extend([1, 0])  # LHP=1, RHP=0
                            if bats_overall == "Both":
                                bats_overall = "Right"
                        else:
                            prediction_input.extend([0, 1])  # LHP=0, RHP=1
                            if bats_overall == "Both":
                                bats_overall = "Left"

                        headers = ["AVG", "OBP%", "SLG%", "SO/BB"]

                        for j in range(len(headers)):
                            if prediction_input[1]:  # away game for batter, get home info for pitcher
                                prediction_input.append(pitcher_splits.ix[opp_pitcher, headers[j] + " - Home"])
                            else:  # home game for batter, get away info for pitcher
                                prediction_input.append(pitcher_splits.ix[opp_pitcher, headers[j] + " - Away"])
                            if bats_overall == "Left":
                                prediction_input.append(pitcher_splits.ix[opp_pitcher, headers[j] + " - LHB"])
                            else:
                                prediction_input.append(pitcher_splits.ix[opp_pitcher, headers[j] + " - RHB"])

                        print(prediction_input)
                        random_forest = joblib.load("models/batters/" + batter + ".mdl")
                        predicted_points = random_forest.predict(prediction_input)
                        batter_df.ix[batter, "Points"] = predicted_points
                        print(predicted_points)

        for pitcher in active_pitchers:
            print(pitcher)
            if pitcher + ".mdl" not in pitcher_models or pitcher not in list(pitcher_splits.index.values):  # skip, default to original value
                continue
            else:
                current_tuple = ""
                for pt in pitcher_tuples:
                    if pitcher == pt[0]:  # name match
                        current_tuple = pt
                        break
                if not current_tuple:  # no gameday info, skip
                    continue
                else:  # we found a tuple, extract information
                    print(current_tuple)
                    # sample tuple: ('Chris Sale', 'Away', ['Ian Kinsler', 'Nick Castellanos',
                    # 'Miguel Cabrera', 'Victor Martinez', 'Justin Upton', 'Mikie Mahtook',
                    # 'James McCann', 'JaCoby Jones', 'Jose Iglesias'])

                    headers = ["AVG", "BB/K", "GB/FB", "OPS"]
                    # Away | Home | AVG_HA | AVG_LR | BB_K_HA | BB_K_LR | GB_FB_HA | GB_FB_LR | OPS_HA | OPS_LR
                    prediction_input = []
                    throws = pitcher_splits.ix[pitcher, "Throws:"]

                    if current_tuple[1] == "Away":
                        prediction_input.extend([1, 0])  # Away=1, Home=0
                    else:
                        prediction_input.extend([0, 1])  # Away=0, Home=1

                    offset = len(prediction_input)

                    prediction_input.extend([0] * 8)  # placeholder for the remaining positions

                    batter_count = 0
                    for batter in current_tuple[2]:
                        if batter in list(batter_splits.index.values):
                            batter_count += 1
                            print(batter)

                            for j in range(len(headers)):
                                if prediction_input[0]:  # away game for pitcher, get home info for batters
                                    prediction_input[offset+2*j] += batter_splits.ix[batter, headers[j] + " - Home"]
                                else:
                                    prediction_input[offset+2*j] += batter_splits.ix[batter, headers[j] + " - Away"]

                                if throws == "Left":
                                    prediction_input[offset+2*j+1] += batter_splits.ix[batter, headers[j] + " - LHP"]
                                else:
                                    prediction_input[offset+2*j+1] += batter_splits.ix[batter, headers[j] + " - RHP"]

                    for i in range(offset, len(prediction_input)):
                        prediction_input[i] /= batter_count

                    print(prediction_input)
                    random_forest = joblib.load("models/pitchers/" + pitcher + ".mdl")
                    predicted_points = random_forest.predict(prediction_input)
                    pitcher_df.ix[pitcher, "Points"] = predicted_points
                    print(predicted_points)

        os.chdir("daily_rfr_projections/" + formatted_date)
        with open("batter_projections_" + formatted_date + ".data", "wb") as dli:
            pickle.dump(batter_df, dli)

        with open("pitcher_projections_" + formatted_date + ".data", "wb") as dli:
            pickle.dump(pitcher_df, dli)
        os.chdir("../..")

    return batter_df, pitcher_df


"""get_current_date():

Formats current date in appropriate order.

Returns string with the formatted date.

"""


def get_current_date():
    current_date = str(datetime.datetime.now()).split(' ')[0]
    current_year, current_month, current_day = current_date.split('-')
    formatted_date = str(current_month + current_day + current_year)
    return formatted_date


"""get_lineups(return_tuples=False, headless=True, verbose=True):

Scrapes FantasyLabs for present day's MLB lineups.

Args:
    headless: True indicates PhantomJS browser, False indicates visible Firefox browser.
    verbose: True indicates printing all messages as the function operates, False indicates silent operation.
    return_tuples: True indicates returning tuples with detailed information about player matchup, False indicates name only.

Returns list of players who are active for the day. Pickles detailed tuples and plain name lists for the day.

"""


def get_lineups(return_tuples=False, headless=True, verbose=True):
    print(os.getcwd())
    os.chdir("daily_lineup_info")
    formatted_date = get_current_date()

    all_batters = []
    all_pitchers = []

    pitcher_tuples = []
    batter_tuples = []

    if os.path.isdir(formatted_date):
        os.chdir(formatted_date)
        if verbose:
            print("Lineups already downloaded, loading from pickled data.")

        with open("batter_tuples_" + formatted_date + ".data", "rb") as dli:
            batter_tuples = pickle.load(dli)

        with open("pitcher_tuples_" + formatted_date + ".data", "rb") as dli:
            pitcher_tuples = pickle.load(dli)

        with open("batter_names_" + formatted_date + ".data", "rb") as dli:
            all_batters = pickle.load(dli)

        with open("pitcher_names_" + formatted_date + ".data", "rb") as dli:
            all_pitchers = pickle.load(dli)
        os.chdir("..")

    else:
        if verbose:
            print("Loading browser...")

        browser = browser_initialization(headless)

        if verbose:
            print("Connecting to FantasyLabs for line-ups on " + formatted_date + "...")

        fl_link = "http://www.fantasylabs.com/mlb/lineups/?date=" + formatted_date
        browser.get(fl_link)

        if verbose:
            print("Link of lineups can be found at " + fl_link + ".")
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

            order = 1
            for b in batters_away:
                all_batters.append(b.find_element_by_tag_name("span").text)
                batter_tuples.append((all_batters[-1], order, "Away", all_pitchers[-1]))
                order += 1

            pitcher_tuples.append((all_pitchers[-1], "Home", all_batters[-9:]))

            if verbose:
                print("\nAway Batting Lineup:")
                for i in range(len(batters_away)):
                    print(str(i+1) + ". " + all_batters[(i-9)])

            order = 1
            batters_home = projected_lineups[1].find_elements_by_tag_name("li")
            for b in batters_home:
                all_batters.append(b.find_element_by_tag_name("span").text)
                batter_tuples.append((all_batters[-1], order, "Home", all_pitchers[-2]))
                order += 1

            pitcher_tuples.append((all_pitchers[-2], "Away", all_batters[-9:]))

            if verbose:
                print("\nHome Batting Lineup:")
                for i in range(len(batters_home)):
                    print(str(i+1) + ". " + all_batters[i-9])

        os.mkdir(formatted_date)
        os.chdir(formatted_date)

        with open("batter_tuples_" + formatted_date + ".data", "wb") as dli:
            pickle.dump(batter_tuples, dli)

        with open("pitcher_tuples_" + formatted_date + ".data", "wb") as dli:
            pickle.dump(pitcher_tuples, dli)

        with open("batter_names_" + formatted_date + ".data", "wb") as dli:
            pickle.dump(all_batters, dli)

        with open("pitcher_names_" + formatted_date + ".data", "wb") as dli:
            pickle.dump(all_pitchers, dli)

        os.chdir("..")

    os.chdir("..")

    if return_tuples:
        return pitcher_tuples, batter_tuples
    else:
        return all_pitchers, all_batters
