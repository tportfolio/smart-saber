__author__ = 'Timothy'

import pickle
import os
import time
import csv
import pandas as pd
import collections

from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.action_chains import ActionChains


def batter_br_list_scraper(browser):
    browser.get("http://www.baseball-reference.com/leagues/MLB/2016-standard-batting.shtml")
    browser.execute_script("window.scrollTo(0, 1250)")
    browser.find_element_by_id("players_standard_batting_toggle_partial_table").click()
    qual = browser.find_elements_by_class_name("full_table")

    batter_links = []
    for el in qual:
        pa = int(el.find_element_by_xpath("td[6]").text)
        if pa > 200:  # cutoff for relevant number of PAs
            link_column = el.find_element_by_class_name("left")
            link_location = link_column.find_element_by_tag_name("a")
            batter_name = link_location.text
            link_split = link_location.get_attribute("href").split('/')
            name_id = link_split[-1].rsplit('.')[0]
            batting_2016 = "http://www.baseball-reference.com/players/gl.fcgi?id=" + name_id + "&t=b&year=2016"

            print(batter_name + " - " + batting_2016 + " - " + str(pa))
            batter_links.append((batter_name, batting_2016))

    with open("batter_links_br.data", "wb") as bl:
        pickle.dump(batter_links, bl)
    print(len(qual))


def batter_fg_list_scraper(browser):
    browser.get("http://www.fangraphs.com/leaders.aspx?pos=all&stats=bat&lg=all&qual=0&type=8&season=2016&month=0&season1=2016&ind=0&team=0&rost=0&age=0&filter=&players=0&sort=4,d&page=1_352")
    entries = browser.find_elements_by_xpath("/html/body/form/div[3]/div[2]/span[2]/div/table/tbody/tr")
    print(len(entries))

    batters = []
    for entry in entries:
        url = entry.find_element_by_tag_name("a")
        batters.append((url.text, url.get_attribute("href")))

        print(batters[-1])

    with open("batter_links_fg.data", "wb") as bl:
        pickle.dump(batters, bl)


def batter_br_csv_scraper(browser):
    bl = open("batter_links_br.data", "rb")
    batters = pickle.load(bl)
    bl.close()

    os.chdir("../scraping/batting/baseball-reference")

    for batter in batters:
        if batter[0] + ".csv" in os.listdir(os.getcwd()):
            continue
        print(batter)
        browser.get(batter[1])
        time.sleep(5)

        dropdowns = browser.find_elements_by_class_name("hasmore")
        share_and_more = dropdowns[-1]
        scroll_buffer = browser.find_element_by_xpath("/html/body/div[2]/div[5]/div[2]/div[2]/div[2]/h3")
        browser.execute_script("return arguments[0].scrollIntoView();", scroll_buffer)
        ActionChains(browser).move_to_element(share_and_more).perform()
        time.sleep(2)

        options = share_and_more.find_elements_by_tag_name("li")
        options[3].click()  # CSV option
        csv_table = browser.find_element_by_id("csv_batting_gamelogs")
        print(csv_table.text)

        with open(batter[0] + ".csv", "w") as sl:
            sl.write(csv_table.text)


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

def pitcher_br_list_scraper(browser):
    browser.get("http://www.baseball-reference.com/leagues/MLB/2016-standard-pitching.shtml")
    browser.execute_script("window.scrollTo(0, 1250)")
    browser.find_element_by_id("players_standard_pitching_toggle_partial_table").click()
    qual = browser.find_elements_by_class_name("full_table")

    pitcher_links = []
    for el in qual:
        gs = int(el.find_element_by_xpath("td[10]").text)
        if gs >= 12:  # cutoff for relevant number of GSs
            link_column = el.find_element_by_class_name("left")
            link_location = link_column.find_element_by_tag_name("a")
            pitcher_name = link_location.text
            link_split = link_location.get_attribute("href").split('/')
            name_id = link_split[-1].rsplit('.')[0]
            pitching_2016 = "http://www.baseball-reference.com/players/gl.fcgi?id=" + name_id + "&t=p&year=2016"

            print(pitcher_name + " - " + pitching_2016 + " - " + str(gs))
            pitcher_links.append((pitcher_name, pitching_2016))

    with open("pitcher_links_br.data", "wb") as bl:
        pickle.dump(pitcher_links, bl)
    print(len(qual))


def pitcher_br_csv_scraper(browser):

    pl = open("pitcher_links_br.data", "rb")
    pitchers = pickle.load(pl)
    pl.close()

    os.chdir("../scraping/pitching/baseball-reference")

    for pitcher in pitchers:
        if pitcher[0] + ".csv" in os.listdir(os.getcwd()):
            continue
        print(pitcher)
        browser.get(pitcher[1])
        time.sleep(5)

        dropdowns = browser.find_element_by_class_name("section_heading_text")
        share_and_more = dropdowns.find_element_by_class_name("hasmore")
        #scroll_buffer = browser.find_element_by_tag_name("h2")
        #browser.execute_script("return arguments[0].scrollIntoView();", scroll_buffer)
        ActionChains(browser).move_to_element(share_and_more).perform()
        time.sleep(2)

        options = share_and_more.find_elements_by_tag_name("li")
        options[3].click()  # CSV option
        csv_table = browser.find_element_by_id("csv_pitching_gamelogs")
        print(csv_table.text)

        with open(pitcher[0] + ".csv", "w") as sl:
            sl.write(csv_table.text)

def throw_type_scraper(browser):
    os.chdir("../scraping/pitching/pitcher_profiles")
    all_pitchers = collections.OrderedDict()

    browser.get("http://www.baseball-reference.com/leagues/MLB/2016-standard-pitching.shtml")
    browser.execute_script("window.scrollTo(0, 1250)")
    browser.find_element_by_id("players_standard_pitching_toggle_partial_table").click()
    pitcher_list = browser.find_elements_by_class_name("full_table")

    pitcher_urls = []
    for pitcher in pitcher_list:
        gs = int(pitcher.find_element_by_xpath("td[10]").text)
        if gs >= 12:  # cutoff for relevant number of GSs
            link_column = pitcher.find_element_by_class_name("left")
            link_location = link_column.find_element_by_tag_name("a")
            pitcher_name = link_location.text
            link = link_location.get_attribute("href")
            pitcher_urls.append((pitcher_name, link))
            print(pitcher_urls[-1])

    with open("pitcher_links_used.data", "wb") as ul:
        pickle.dump(pitcher_urls, ul)

    for pitcher in pitcher_urls:
        pitcher_dict = collections.OrderedDict()
        browser.get(pitcher[1])

        try:
            throw_type = browser.find_element_by_xpath("/html/body/div[2]/div[2]/div[1]/div[2]/p[2]")
        except:
            throw_type = browser.find_element_by_xpath("/html/body/div[2]/div[2]/div[1]/div/p[2]")

        throws = throw_type.text.split(' ')[-1]
        print(pitcher[0] + ' - ' + throws)
        pitcher_dict["Throws:"] = throws
        all_pitchers[pitcher[0]] = pitcher_dict

    with open("pitcher_profiles.data", "wb") as pl:
        pickle.dump(all_pitchers, pl)

def pitcher_br_split_scraper(browser):

    os.chdir("../scraping/pitching/pitcher_profiles")
    pl = open("pitcher_links_used.data", "rb")
    pitchers = pickle.load(pl)
    print(len(pitchers))
    pl.close()

    pd = open("pitcher_profiles.data", "rb")
    dicts = pickle.load(pd)
    pd.close()

    for pitcher in pitchers:
        print(pitcher)
        p_dict = dicts[pitcher[0]]
        pitcher_id = pitcher[1].split('/')[-1].rsplit('.', 1)[0]
        browser.get("http://www.baseball-reference.com/players/split.fcgi?id=" + pitcher_id + "&year=2016&t=p")
        platoon_splits = browser.find_element_by_id("all_plato").find_element_by_tag_name("tbody")

        rhb_sobb = platoon_splits.find_element_by_xpath("tr[1]/td[13]").text
        p_dict["SO/BB - RHB"] = float(rhb_sobb)

        rhb_avg = platoon_splits.find_element_by_xpath("tr[1]/td[14]").text
        p_dict["AVG - RHB"] = float(rhb_avg)

        rhb_obp = platoon_splits.find_element_by_xpath("tr[1]/td[15]").text
        p_dict["OBP% - RHB"] = float(rhb_obp)

        rhb_slg = platoon_splits.find_element_by_xpath("tr[1]/td[16]").text
        p_dict["SLG% - RHB"] = float(rhb_slg)

        lhb_sobb = platoon_splits.find_element_by_xpath("tr[2]/td[13]").text
        p_dict["SO/BB - LHB"] = float(lhb_sobb)

        lhb_avg = platoon_splits.find_element_by_xpath("tr[2]/td[14]").text
        p_dict["AVG - LHB"] = float(lhb_avg)

        lhb_obp = platoon_splits.find_element_by_xpath("tr[2]/td[15]").text
        p_dict["OBP% - LHB"] = float(lhb_obp)

        lhb_slg = platoon_splits.find_element_by_xpath("tr[2]/td[16]").text
        p_dict["SLG% - LHB"] = float(lhb_slg)

        home_away_splits = browser.find_element_by_id("all_hmvis").find_element_by_tag_name("tbody")

        home_sobb = home_away_splits.find_element_by_xpath("tr[1]/td[13]").text
        p_dict["SO/BB - Home"] = float(home_sobb)

        home_avg = home_away_splits.find_element_by_xpath("tr[1]/td[14]").text
        p_dict["AVG - Home"] = float(home_avg)

        home_obp = home_away_splits.find_element_by_xpath("tr[1]/td[15]").text
        p_dict["OBP% - Home"] = float(home_obp)

        home_slg = home_away_splits.find_element_by_xpath("tr[1]/td[16]").text
        p_dict["SLG% - Home"] = float(home_slg)

        away_sobb = home_away_splits.find_element_by_xpath("tr[2]/td[13]").text
        p_dict["SO/BB - Away"] = float(away_sobb)

        away_avg = home_away_splits.find_element_by_xpath("tr[2]/td[14]").text
        p_dict["AVG - Away"] = float(away_avg)

        away_obp = home_away_splits.find_element_by_xpath("tr[2]/td[15]").text
        p_dict["OBP% - Away"] = float(away_obp)

        away_slg = home_away_splits.find_element_by_xpath("tr[2]/td[16]").text
        p_dict["SLG% - Away"] = float(away_slg)

        for key in p_dict.keys():
            print(key + " - " + str(p_dict[key]))

    with open("pitcher_profiles_updated.data", "wb") as ppu:
        pickle.dump(dicts, ppu)

def batter_type_scraper(browser):
    os.chdir("../scraping/batting/batter_profiles")
    all_batters = collections.OrderedDict()

    browser.get("http://www.baseball-reference.com/leagues/MLB/2016-standard-batting.shtml")
    browser.execute_script("window.scrollTo(0, 1250)")
    browser.find_element_by_id("players_standard_batting_toggle_partial_table").click()
    batter_list = browser.find_elements_by_class_name("full_table")

    batter_urls = []
    for batter in batter_list:
        pa = int(batter.find_element_by_xpath("td[6]").text)
        if pa >= 50:  # filters out relievers/unused players
            link_column = batter.find_element_by_class_name("left")
            link_location = link_column.find_element_by_tag_name("a")
            batter_name = link_location.text
            link = link_location.get_attribute("href")
            batter_urls.append((batter_name, link))
            print(batter_urls[-1])

    with open("batter_links_used.data", "wb") as ul:
        pickle.dump(batter_urls, ul)

    for batter in batter_urls:
        batter_dict = collections.OrderedDict()
        browser.get(batter[1])

        try:
            bat_type = browser.find_element_by_xpath("/html/body/div[2]/div[2]/div[1]/div[2]/p[2]")
        except:
            bat_type = browser.find_element_by_xpath("/html/body/div[2]/div[2]/div[1]/div/p[2]")

        bats = bat_type.text.split(' ')[1]
        print(batter[0] + ' - ' + bats)
        batter_dict["Bats:"] = bats
        all_batters[batter[0]] = batter_dict

    with open("batter_profiles.data", "wb") as bl:
        pickle.dump(all_batters, bl)

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

def box_score_link_scraper(browser):
    browser.get("http://www.baseball-reference.com/leagues/MLB/2016-schedule.shtml")
    boxscore_list = browser.find_element_by_id("div_2006060273").find_elements_by_link_text("Boxscore")
    print(len(boxscore_list))
    boxscores = [el.get_attribute("href") for el in boxscore_list]
    with open("boxscores.data", "wb") as bs:
        pickle.dump(boxscores, bs)

def box_score_collector(browser):
    box_score_dicts = collections.OrderedDict()
    with open("boxscores.data", "rb") as bs:
        box_scores = pickle.load(bs)
        for box_score in box_scores:
            current_bs_dict, away_lineup, home_lineup = (collections.OrderedDict() for i in range(3))
            browser.get(box_score)
            print(box_score)

            away = browser.find_element_by_id("lineups_1").find_elements_by_tag_name("tr")
            home = browser.find_element_by_id("lineups_2").find_elements_by_tag_name("tr")

            batters = []
            pitcher = ""
            for player in away:
                cols = player.find_elements_by_tag_name("td")
                try:
                    name = cols[1].find_element_by_tag_name("a").text
                except:
                    name = ""
                if cols[0].text != "":
                    batters.append(name)
                if cols[2].text == "P":
                    pitcher = name
            away_lineup["Pitcher"] = pitcher
            away_lineup["Batters"] = batters

            current_bs_dict["Away"] = away_lineup

            batters = []
            pitcher = ""
            for player in home:
                cols = player.find_elements_by_tag_name("td")
                try:
                    name = cols[1].find_element_by_tag_name("a").text
                except:
                    name = ""
                if cols[0].text != "":
                    batters.append(name)
                if cols[2].text == "P":
                    pitcher = name
            home_lineup["Pitcher"] = pitcher
            home_lineup["Batters"] = batters

            current_bs_dict["Home"] = home_lineup
            print(home_lineup["Batters"])
            print(home_lineup["Pitcher"])

            game_id = box_score.split('/')[-1].strip(".shtml")
            print(game_id)
            box_score_dicts[game_id] = current_bs_dict

        with open("box_scores_dicts.data", "wb") as bsd:
            pickle.dump(box_score_dicts, bsd)

def batter_df_initialization():
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

def pitching_profiles_to_df():
    os.chdir("../scraping/pitching/pitcher_profiles")
    pp = open("pitcher_profiles_updated.data", "rb")
    pitcher_profiles = pickle.load(pp)
    pp.close()

    df = pd.DataFrame.from_dict(pitcher_profiles).transpose()
    print(df)

    with open("pitchers.dframe", "wb") as pdf:
        pickle.dump(df, pdf)

def batting_profiles_to_df():
    os.chdir("../scraping/batting/batter_profiles")
    pp = open("batter_profiles_updated.data", "rb")
    batter_profiles = pickle.load(pp)
    pp.close()

    df = pd.DataFrame.from_dict(batter_profiles).transpose()
    print(df)

    pp = open("batter_profiles.data", "rb")
    batter_profiles = pickle.load(pp)
    pp.close()
    df2 = pd.DataFrame.from_dict(batter_profiles).transpose()
    print(df2)

    final_df = pd.concat([df, df2], axis=1, join_axes=[df.index])
    print(final_df)

    with open("batters.dframe", "wb") as pdf:
        pickle.dump(df, pdf)

def box_scores_to_df():
    bs = open("box_scores_dicts.data", "rb")
    batter_profiles = pickle.load(bs)
    bs.close()
    df = pd.DataFrame.from_dict(batter_profiles).transpose()
    print(df)
    with open("box_scores.dframe", "wb") as bsdf:
        pickle.dump(df, bsdf)



def main():
    # binary = FirefoxBinary(r'C:\Program Files\Mozilla Firefox 46\firefox.exe')
    # fp = webdriver.FirefoxProfile(r'C:\Users\Timothy\AppData\Roaming\Mozilla\Firefox\Profiles\d9ra2s92.selenium')
    # browser = webdriver.Firefox(firefox_binary=binary, firefox_profile=fp)

    # os.chdir("../scraping/pitching/pitcher_profiles")
    # pp = open("pitchers.dframe", "rb")
    # pitcher_profiles = pickle.load(pp)
    # pp.close()
    #
    # print(pitcher_profiles.head())
    # print(pitcher_profiles.ix["Tim Adleman"])



    #
    os.chdir("batting/batter_profiles")

    for link in links:
        print(link[0])
        browser.get(link[1])

        game_list = browser.find_element_by_id("batting_gamelogs")
        games = game_list.find_elements_by_css_selector("[id^=batting_gamelogs]")
        print(len(games))

        with open(link[0] + ".dframe", "rb") as dff:
            df = pickle.load(dff)
            df = df.assign(LHP=0, RHP=0)
            print(df)

            for i in range(len(games)):
                game_id = games[i].find_element_by_xpath("td[3]").find_element_by_tag_name("a").get_attribute("href")
                game_id = game_id.split('/')[-1].strip(".shtml")
                print(game_id)

                box_score = box_scores[game_id]
                if df.ix[i, "Away"] == 1:



                points = games[i].find_element_by_xpath("td[35]").text
                print(points)

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


    #http://stackoverflow.com/questions/41644381/python-set-firefox-preferences-for-selenium-download-location/41683377#41683377

if __name__ == "__main__":
    main()