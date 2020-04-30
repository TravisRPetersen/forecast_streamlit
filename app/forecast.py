import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import streamlit as st
from os.path import dirname, join, realpath


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

def streamlit_dataframe(results, team_list):
    st.subheader("Team ratings are an average of player subgroup ratings\nExplore those ratings by team here")

    #filter_table = filter_results(results, number_of_rows, number_of_columns, style)
    TEAMS_SELECTED = st.multiselect('Select team', team_list)
    # Mask to filter dataframe
    mask_teams = results['team_name'].isin(TEAMS_SELECTED)
    results = results[mask_teams].reset_index(drop=True)

    st.dataframe(results)

def main():

    page = st.sidebar.selectbox("Page", ["Projections & Depth Charts", "Player Value", "Depth Chart Image"])
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
        st.image(f"https://storage.googleapis.com/baseball-forecast/kbo_depth_charts/{kbo_team}.png", width=200)

main()