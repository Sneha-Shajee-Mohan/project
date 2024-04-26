import os
import streamlit as st
from dotenv import load_dotenv
from utils.b2 import B2
import folium
from streamlit_folium import folium_static
import pandas as pd
import requests
from utils.explore import ParkExplorer



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
    # collect data frame 
    b2.set_bucket(os.environ['B2_BUCKETNAME'])
    df = b2.get_df(REMOTE_DATA)
    
    return df

# ------------------------------------------------------
#                         APP
# ------------------------------------------------------
# df_park = get_data()

# testing class
class TestDisplayFeeInfo:
    def test_failed_to_fetch_api(self):
        expected_output = "Failed to fetch fees"
        self.assertEqual(ParkExplorer.fetch_fee("abcd"), expected_output)


# For styling i gave black background with white fonts
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
    # select a state and corresponding park
    st.markdown("<h5 style='color: white;'>Select a state:</h5>", unsafe_allow_html=True)
    selected_state = st.selectbox("",df_park['address_stateCode'].unique())
    st.markdown("<h5 style='color: white;'>Select a Park:</h5>", unsafe_allow_html=True)
    parks_in_state = park_explorer.get_parks_in_state(selected_state)

    # Display park selection dropdown
    park_name = st.selectbox("", parks_in_state)

    #code for showing alerts in park
    park_code = df_park[df_park['fullName'] == park_name]['parkCode'].iloc[0]
    
    alerts = park_explorer.fetch_alerts(park_code)
    if alerts:
        st.subheader("Alerts")
        for alert in alerts:
            st.write(f"Category: {alert['category']}")
            st.write(f"Description: {alert['description']}")
            st.write("---")

    # Displaying park details
    park_explorer.display_park_details(park_name)
 
    st.subheader("Explore additional information about the park!")
    # setting tabs for better user interface

    tab1, tab2, tab3, tab4, tab5 = st.tabs([":green[Directions]", ":green[Weather]", ":green[Contact]", ":green[Map]", ":green[Gallery]"])
    
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

    #code for showing park fee details
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
  

       
