import os
import pickle

from sklearn.ensemble import RandomForestRegressor
from sklearn.externals import joblib


def create_clfs(player_type):
    na = open("finalized_data_structures/" + player_type + "_game_logs_2016.data", "rb")
    df_dict = pickle.load(na)
    na.close()

    os.chdir("models/" + player_type + "s")
    players = df_dict.keys()

    for player in players:
        df = df_dict[player]
        print(player)

        if player_type == "pitcher":
            df = df.drop("Points_Last5", 1)
            df = df.drop("DR", 1)

        print(df.head())
        if player_type == "batter":
            df = df[(df.RHP == 1) | (df.LHP == 1)]
            try:
                df['Points'] = df['Points'].astype(float)
            except ValueError:  # skip over dataframe in case of conversion error
                continue
            df = df[df.Points < df.Points.quantile(.95)]

        print(df['Points'].describe())
        points = df["Points"]
        training_data = df.drop("Points", 1)
        forest = RandomForestRegressor(n_estimators=1000, max_depth=50,
                                       min_samples_split=10, n_jobs=-1)
        forest.fit(training_data, points)
        print("Fit: " + str(forest.score(training_data, points)))
        joblib.dump(forest, player + ".mdl")


