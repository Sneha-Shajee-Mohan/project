import os
import streamlit as st
from dotenv import load_dotenv
from utils.b2 import B2
import folium
from streamlit_folium import folium_static
import pandas as pd
import requests



# ------------------------------------------------------
#                      APP CONSTANTS
# ------------------------------------------------------
REMOTE_DATA = 'NPS.ipynbnational_parks.csv'


# ------------------------------------------------------
#                        CONFIG
# ------------------------------------------------------
load_dotenv()

# load Backblaze connection
b2 = B2(endpoint=os.environ['B2_ENDPOINT'],
        key_id=os.environ['B2_KEYID'],
        secret_key=os.environ['B2_APPKEY'])

# ------------------------------------------------------
#                        CACHING
# ------------------------------------------------------
@st.cache_data
def get_data():
#     # collect data frame of reviews and their sentiment
    b2.set_bucket(os.environ['B2_BUCKETNAME'])
    df = b2.get_df(REMOTE_DATA)
    
    return df

# ------------------------------------------------------
#                         APP
# ------------------------------------------------------
df_park = get_data()

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
        
class TestDisplayFeeInfo:
    def test_failed_to_fetch_api(self):
        expected_output = "Failed to fetch fees"
        self.assertEqual(ParkExplorer.fetch_fee("abcd"), expected_output)

def main():
    st.title("National Park Explorer")
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #202020;
            font-color: #FFFFF   
        }
        .stMarkdown > div > p {
        color: white 
        }
        h1,h2,h3,h4,h5,h6,h7,h8,h9 {
        color: #FFFFFF; 
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Load park data
    df_park = get_data()

    # Create ParkExplorer object
    park_explorer = ParkExplorer(df_park)
    st.markdown("<h5 style='color: white;'>Select a state:</h5>", unsafe_allow_html=True)
    selected_state = st.selectbox("",df_park['address_stateCode'].unique())
    st.markdown("<h5 style='color: white;'>Select a Park:</h5>", unsafe_allow_html=True)
    parks_in_state = park_explorer.get_parks_in_state(selected_state)

    # Display park selection dropdown
    park_name = st.selectbox("", parks_in_state)

    #alerts
    park_code = df_park[df_park['fullName'] == park_name]['parkCode'].iloc[0]
    # st.write(park_code)
    alerts = park_explorer.fetch_alerts(park_code)
    if alerts:
        st.subheader("Alerts")
        for alert in alerts:
            st.write(f"Category: {alert['category']}")
            st.write(f"Description: {alert['description']}")
            st.write("---")

    # Display park details
    park_explorer.display_park_details(park_name)
 
    st.subheader("Explore additional information about the park!")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([":green[Directions]", ":green[Weather]", ":green[Contact]", ":green[Map]", ":green[Gallery]"])
    # Display other features
    # if st.checkbox(":green[Display Directions]"):
    #     park_explorer.display_direction(park_name)

    # if st.checkbox(":green[Display Weather Info]"):
    #     park_explorer.display_weather_info(park_name)

    # if st.checkbox(":green[Display Contact Info]"):
    #     park_explorer.display_contact_info(park_name)

    # if st.checkbox(" :green[Display Interactive Map]"):
    #     park_explorer.display_interactive_map(park_name)

    # if st.checkbox(" :green[Display Multimedia]"):
    #     park_explorer.display_multimedia(park_name)

    with tab1:
        st.header("Direction information")
        park_explorer.display_direction(park_name)

    with tab2:
        st.header("Weather details")
        park_explorer.display_weather_info(park_name)

    with tab3:
        st.header("Contact Information")
        park_explorer.display_contact_info(park_name)

    with tab4:
        st.header("Get a little help with Maps")
        park_explorer.display_interactive_map(park_name)

    with tab5:
        st.header("Gallery")
        park_explorer.display_multimedia(park_name)


    fees = park_explorer.fetch_fee(park_code)
    if fees:
    
        # st.subheader("Fee Details")
            for fee in fees:
             
                if fee['entranceFeeDescription']:
                    with st.popover(":red[show fee details]"):
                        st.write(f":green[{fee['entranceFeeDescription']}]")
                else:
                    with st.popover(":red[show fee details]"):
                        st.write(":green[No information available]")
                


if __name__ == "__main__":
    main()
  

       
