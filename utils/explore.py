import os
import streamlit as st
from dotenv import load_dotenv
from utils.b2 import B2
import folium
from streamlit_folium import folium_static
import pandas as pd
import requests


class ParkExplorer:
    def __init__(self, df):
        self.df = df

    def get_parks_in_state(self, state):
        return self.df[self.df['states'] == state]['fullName'].tolist()    

    def display_park_details(self, park_name):
        park = self.df[self.df['fullName'] == park_name]
        st.subheader(park_name)
        st.write("Description:", park['description'].values[0])
        
    def display_direction(self, park_name):
        park = self.df[self.df['fullName'] == park_name]
        # st.subheader("Directions")
        st.write(park['directionsInfo'].values[0])

    def display_weather_info(self, park_name):
        park = self.df[self.df['fullName'] == park_name]
        # st.subheader("Weather Info")
        st.write(park['weatherInfo'].values[0])

    def display_contact_info(self, park_name):
        park = self.df[self.df['fullName'] == park_name]
        # st.subheader("Contact Info")
        st.write("Phone Number:", park['park_phoneNumber'].values[0])
        st.write("Email Address:", park['park_emailAddress'].values[0])

    def display_interactive_map(self, park_name):
        park = self.df[self.df['fullName'] == park_name]
        map_center = (park['latitude'], park['longitude'])
        m = folium.Map(location=map_center, zoom_start=10)
        folium.Marker(location=map_center, popup=park_name).add_to(m)
        folium_static(m)

    def display_multimedia(self, park_name):
        park = self.df[self.df['fullName'] == park_name]
        
        images_urls = park['images_url'].values[0]  
       
        st.image(images_urls, caption='', use_column_width=True)
        
    def fetch_alerts(self,park_code):
        on = st.toggle(" :red[show Alerts]")
        if on:
            try:
                key = os.environ['api_key']
                url = f"https://developer.nps.gov/api/v1/alerts?parkCode={park_code}&api_key={key}"
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    return data["data"]
                else:
                    st.error("Failed to fetch alerts")
                    return None
            except Exception as e:
                st.error(f"An error occurred: {e}")
                return None
            

    def fetch_fee(self,park_code):
        
        try:
                key = os.environ['api_key']
                url = f"https://developer.nps.gov/api/v1/feespasses?parkCode={park_code}&api_key={key}"
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    return data["data"]
                else:
                    st.error("Failed to fetch fees")
                    return None
        except Exception as e:
            st.error(f"An error occurred: {e}")
            return None
