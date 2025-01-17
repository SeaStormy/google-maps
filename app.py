import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import time

# Configure the page
st.set_page_config(page_title="Simple Maps App", layout="wide")

# Initialize session state for search history
if 'search_history' not in st.session_state:
    st.session_state.search_history = []


def geocode_address(address):
    """
    Geocode an address using Nominatim with error handling and rate limiting
    """
    try:
        # Rate limiting to avoid hitting API limits
        time.sleep(1)
        geolocator = Nominatim(user_agent="my_streamlit_app")
        location = geolocator.geocode(address)

        if location is None:
            raise ValueError("Location not found")

        return {
            'latitude': location.latitude,
            'longitude': location.longitude,
            'address': location.address
        }

    except GeocoderTimedOut:
        st.error("Error: The geocoding service timed out. Please try again.")
        return None
    except GeocoderUnavailable:
        st.error(
            "Error: The geocoding service is currently unavailable. Please try again later.")
        return None
    except ValueError as e:
        st.error(f"Error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        return None


def create_map(location=None, zoom_start=13):
    """
    Create a Folium map centered on the specified location
    """
    if location:
        m = folium.Map(
            location=[location['latitude'], location['longitude']],
            zoom_start=zoom_start
        )
        # Add marker for the searched location
        folium.Marker(
            [location['latitude'], location['longitude']],
            popup=location['address'],
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
    else:
        # Default view (world map)
        m = folium.Map(location=[0, 0], zoom_start=2)

    return m


def main():
    st.title("🗺️ Simple Maps Application")

    # Search box
    search_query = st.text_input("Enter location to search:", "")

    col1, col2 = st.columns([2, 1])

    with col1:
        if search_query:
            location_data = geocode_address(search_query)

            if location_data:
                # Add to search history
                if location_data['address'] not in st.session_state.search_history:
                    st.session_state.search_history.append(
                        location_data['address'])

                # Create and display map
                m = create_map(location_data)
                folium_static(m, width=800)

                # Display location details
                st.subheader("Location Details")
                st.write(f"📍 Address: {location_data['address']}")
                st.write(
                    f"📌 Coordinates: {location_data['latitude']:.6f}, {location_data['longitude']:.6f}")
        else:
            # Show default world map
            m = create_map()
            folium_static(m, width=800)

    with col2:
        # Search history
        st.subheader("Search History")
        if st.session_state.search_history:
            for idx, address in enumerate(reversed(st.session_state.search_history), 1):
                st.text(f"{idx}. {address}")
        else:
            st.text("No searches yet")

        # Clear history button
        if st.button("Clear History"):
            st.session_state.search_history = []
            st.rerun()  # Updated from experimental_rerun() to rerun()


if __name__ == "__main__":
    main()
