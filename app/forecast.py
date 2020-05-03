import pandas as pd
import streamlit as st
from google.cloud import storage
import logging
import json
from os.path import dirname, join, realpath

logger = logging.getLogger(__name__)

DIR_PATH = dirname(realpath(__file__))
TEAM_LIST = {"kbo": ['Doosan-Bears', 'Hanwha-Eagles',
                     'KT-Wiz', 'Kia-Tigers', 'Kiwoom-Heroes',
                     'LG-Twins', 'Lotte-Giants',
                     'NC-Dinos', 'SK-Wyverns',
                     'Samsung-Lions'],
            "mlb": ['arizona-diamondbacks',
                    'atlanta-braves',
                    'baltimore-orioles',
                    'boston-red-sox',
                    'chicago-cubs',
                    'chicago-white-sox',
                    'cincinnati-reds',
                    'cleveland-indians',
                    'colorado-rockies',
                    'detroit-tigers',
                    'houston-astros',
                    'kansas-city-royals',
                    'los-angeles-angels',
                    'los-angeles-dodgers',
                    'miami-marlins',
                    'milwaukee-brewers',
                    'minnesota-twins',
                    'new-york-mets',
                    'new-york-yankees',
                    'oakland-athletics',
                    'philadelphia-phillies',
                    'pittsburgh-pirates',
                    'san-diego-padres',
                    'san-francisco-giants',
                    'seattle-mariners',
                    'st-louis-cardinals',
                    'tampa-bay-rays',
                    'texas-rangers',
                    'toronto-blue-jays',
                    'washington-nationals']
             }

storage_client = storage.Client().create_anonymous_client()
bucket = storage_client.bucket(bucket_name="baseball-forecast", user_project=None)
blob = bucket.blob('kbo_schedule/game_data.json')
game_schedule = json.loads(blob.download_as_string(client=None))

def streamlit_dataframe(results, team_list):
    st.subheader("Team ratings are an average of player subgroup ratings\nExplore those ratings by team here")

    #filter_table = filter_results(results, number_of_rows, number_of_columns, style)
    TEAMS_SELECTED = st.multiselect('Select team', team_list)
    # Mask to filter dataframe
    mask_teams = results['team_name'].isin(TEAMS_SELECTED)
    results = results[mask_teams].reset_index(drop=True)

    st.dataframe(results)

def main():

    page = st.sidebar.selectbox("Page", ["Projections & Depth Charts", "Game Predictions","Player Value", "Depth Chart Image"])
    year = st.sidebar.selectbox("Year", ["2020", "2019"])
    league = st.sidebar.selectbox("League", ["KBO", "MLB"]).lower()


    if page=="Projections & Depth Charts":
        st.title("Projection")
        forecast = pd.read_csv(join(DIR_PATH, f"{league}_forecast_{year}.csv"))[['team_name',
                                                                         'batter_rating','rp_rating',
                                                                         'sp_rating','proj_win_pct']]
        st.dataframe(forecast)

        st.title("Depth Chart")
        results = pd.read_csv(join(DIR_PATH, f'{league}_depth_chart_{year}.csv'))
        streamlit_dataframe(results, TEAM_LIST[league])

    if page=="Player Value":
        st.markdown("Not ready")

    if page=="Depth Chart Image":

        kbo_team = st.sidebar.selectbox("Team", TEAM_LIST['kbo'])
        st.write(kbo_team)
        st.image(f"https://storage.googleapis.com/baseball-forecast/kbo_depth_charts/{kbo_team}.png")

    if page=="Game Predictions":

        date = st.date_input("Game Date").strftime("%Y%m%d")
        try:
            games_on_date = game_schedule[date]

            st.dataframe((pd.DataFrame(games_on_date)
             .T
             .astype({"home_win_proj": float})
             .round(2)
             .rename(columns={"away_team": "Away",
                              "home_team": "Home",
                              "home_win_proj": "Home Win Pct"})
             .reset_index(drop=True)
             .style.format({'Home Win Pct': '{:.0%}'})))
        except Exception as e:
            logger.info(e)
            st.write("No scheduled games for date")

main()