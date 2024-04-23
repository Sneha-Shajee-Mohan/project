import os
import pickle
import streamlit as st
from dotenv import load_dotenv
from utils.b2 import B2
import folium
from streamlit_folium import folium_static
import pandas as pd


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
        st.write("Location:", park['states'].values[0])
        

    def display_direction(self, park_name):
        park = self.df[self.df['fullName'] == park_name]
        st.subheader("Directions")
        st.write(park['directionsInfo'].values[0])

    def display_weather_info(self, park_name):
        park = self.df[self.df['fullName'] == park_name]
        st.subheader("Weather Info")
        st.write(park['weatherInfo'].values[0])

    def display_contact_info(self, park_name):
        park = self.df[self.df['fullName'] == park_name]
        st.subheader("Contact Info")
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
        st.subheader("Multimedia")
        images_urls = park['images_url'].values[0]  # Assuming images are provided as a comma-separated list
        # for image_url in images_urls:
        # st.write(images_urls)
        st.image(images_urls, caption='', use_column_width=True)
        #     try:
        #         image = Image.open(image_url)
        #         st.image(image, caption='', use_column_width=True)
        #     except Exception as e:
        #         st.write(f"Error loading image from URL: {e}")



def main():
    st.title("National Park Explorer")
    st.markdown(
        """
        <style>

        .stApp {
            background-color: #000000;
            font
            
        }
        h1,h2,h3,h4,h5,h6,h7,h8,h9 {
        color: #FFFFFF; 
        }
        .stMarkdown > div > p {
        color: white !important;
        }
        .st-ek {
        color: white !important;
        }
   
        .st-av > div > div {
        color: white !important;
        }
        .st-ax {
        background-color: black !important;
        }
        .stTextInput>div>div>div>input {
            color: #FFFFFF;
        }
        .stButton>button {
            background-color: #6c757d;
            color: white;
        }
        .stCheckbox>div>div>label::before {
            border-color: #FFFFFF;
        }
        .stCheckbox>div>div>label:hover::before {
            background-color: #FFFFFF;
        }
        .stCheckbox>div>div>label::after {
            background-color: #00000;
        }
        .stCheckbox>div>div>div>div {
            color: #00000;
        }
        
        .st-ck {
        background-color: white !important;
        }
        
        </style>
        """,
        unsafe_allow_html=True
    )

    

    # Load park data
    df_park = get_data()

    # Create ParkExplorer object
    park_explorer = ParkExplorer(df_park)
    st.markdown("<h5 style='color: white;'>Select a state</h5>", unsafe_allow_html=True)
    selected_state = st.selectbox("",df_park['address_stateCode'].unique())
    st.markdown("<h5 style='color: white;'>Select a Park:</h5>", unsafe_allow_html=True)
    parks_in_state = park_explorer.get_parks_in_state(selected_state)
    # Display park selection dropdown
    park_name = st.selectbox("", parks_in_state)

    # Display park details
    park_explorer.display_park_details(park_name)
 
    st.subheader("Select below option to know more information!")
    # Display other features
    if st.checkbox(":green[Display Directions]"):
        park_explorer.display_direction(park_name)

    if st.checkbox(":green[Display Weather Info]"):
        park_explorer.display_weather_info(park_name)

    if st.checkbox(":green[Display Contact Info]"):
        park_explorer.display_contact_info(park_name)

    if st.checkbox(" :green[Display Interactive Map]"):
        park_explorer.display_interactive_map(park_name)

    if st.checkbox(" :green[Display Multimedia]"):
        park_explorer.display_multimedia(park_name)

if __name__ == "__main__":
    main()
  

       
