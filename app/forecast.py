import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from google.cloud import storage
import logging
import json
from os.path import dirname, join, realpath
from os import environ

creds_file = json.loads(environ.get("GOOGLE_CREDENTIALS"))
with open('google-credentials.json', 'w') as f:
    json.dump(creds_file, f)

logger = logging.getLogger(__name__)

DIR_PATH = dirname(realpath(__file__))
TEAM_LIST = {"extraliga": ['Arrows-Ostrava',
                           'Kotlarka-Praha',
                           'Eagles-Praha',
                           'Hrosi-Brno',
                           'Draci-Brno',
                           'Tempo-Praha',
                           'Technika-Brno',
                           'Nuclears-Trebic',
                           'Olympia-Blansko',
                           'SABAT-Praha'],
            "kbo": ['Doosan-Bears', 'Hanwha-Eagles',
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

date = (datetime.today() + timedelta(hours=9)).strftime("%Y%m%d")
storage_client = storage.Client().from_service_account_json("google-credentials.json")
bucket = storage_client.bucket(bucket_name="baseball-forecast", user_project=None)

def streamlit_dataframe(results, team_list):
    st.subheader("Team ratings are an average of player subgroup ratings")
    st.markdown(""" 
                 Explore those ratings by team here. The depth charts are a pre-season estimate 
                 and will be updated periodically. Feel free to send me updates 
                 [@TravisRPetersen](https://twitter.com/TravisRPetersen) 
                 """)

    #filter_table = filter_results(results, number_of_rows, number_of_columns, style)
    TEAMS_SELECTED = st.multiselect('Select team', team_list)
    # Mask to filter dataframe
    mask_teams = results['team_name'].isin(TEAMS_SELECTED)
    results = results[mask_teams].reset_index(drop=True)

    st.dataframe(results)

def main():

    page = st.sidebar.selectbox("Page", ["Projections & Depth Charts", "Depth Chart Image", "About"])
    year = st.sidebar.selectbox("Year", ["2020"])
    league = st.sidebar.selectbox("League", ["KBO", "MLB","Extraliga"]).lower()


    if page=="Projections & Depth Charts":
        st.title("Projection")
        if league=="kbo":
            date = (datetime.today() + timedelta(hours=9)).strftime("%Y%m%d")
            projection_url = f"gs://baseball-forecast/projected_standings/{league}_forecast_{year}_{date}.csv"
        else:
            projection_url = f"gs://baseball-forecast/projected_standings/{league}_forecast_{year}.csv"
        forecast = pd.read_csv(projection_url)
        st.dataframe(forecast.style.format({'champion': '{:.1%}',
                                            'playoff_appearance': '{:.1%}',
                                            'proj_win_pct': '{:.3f}',
                                            'projected_wins': '{:.1f}',
                                            'current_wins': '{:.0f}',
                                            'batter_rating': '{:.0f}',
                                            'rp_rating': '{:.0f}',
                                            'sp_rating': '{:.0f}'}
                                           ))
        st.title("Depth Chart")
        results = pd.read_csv(join(DIR_PATH, f'{league}_depth_chart_{year}.csv'))
        streamlit_dataframe(results, TEAM_LIST[league])

    if page=="Player Value":
        st.markdown("Not ready")

    if page=="Depth Chart Image":

        if league=="mlb":
            st.markdown(
                """    
                TBD                    
                    """
            )

        else:

            team = st.sidebar.selectbox("Team", TEAM_LIST[league])
            st.subheader(f"{team}:")
            st.image(f"https://storage.googleapis.com/baseball-forecast/{league}_depth_charts/{team}.png")
            st.subheader("Note:")
            st.markdown(
                """    
                    These depth charts are a pre-season estimate and will not be updated on a regular basis. 
                    Starting pitchers are on the left-side of the graphic and relief pitchers on the right-side of the graphic.
                    
                    """
                        )

    if page=="About":
        st.subheader("About:")
        st.markdown(
            """    
                The goal of this app is to give provide a league-level forecast based on player ratings. 
                Player ratings are based on WAR, with 70 as MLB replacement level. 
                WAR estimates are based on a [marcel-style](http://www.tangotiger.net/archives/stud0346.shtml) 
                weighted average of recent seasons using WAR from [kbreport](http://www.kbreport.com/main) 
                and [steamer projections](steamerprojections.com). [MyKBO](https://mykbostats.com/) has been an 
                essential resource for gathering information about depth charts.
                
                A rough guide to the ratings:
                
                *	90: MLB All-Star
                *	80: MLB Starter
                *	70: MLB replacement level
                *	60: AA/AAA
                *	50: A/AA
                *	40: Rk/NCAA-1
                
                The player ratings and forecasts are very much a work in progress and any feedback is welcome!
                
                Notes:
                *	The model does not have access to daily lineups at the moment, so it won’t 
                know if a player is injured or sitting for that day
                *	The lineups are set using best estimates pre-season of lineups
                *	The depth charts only include 21 players (9 batters, 5 starters, and 7 relief pitchers)

                
                """
                )


main()