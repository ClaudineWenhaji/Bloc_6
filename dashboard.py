import streamlit as st

import pandas as pd

import geopandas as gpd

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

import ipywidgets as widgets
from ipywidgets import interact

### CONFIG
st.set_page_config(
    page_title="Medical deserts",
    page_icon="👨‍⚕️",
    layout="wide"
)

### TITLE AND TEXT
st.title("les deserts medicaux en France 👨‍⚕️")

st.markdown("""
    Bienvenu sur le tableau de bord des deserts medicaux ! Vous trouverez sur ce site des informations utiles pour comprendre et identifier les deserts medicaux en France.""")

### LOAD AND CACHE DATA
# URL of the CSV file of APL data
GEO_URL = 'https://medical-deserts-project.s3.eu-north-1.amazonaws.com/geo.geojson'

@st.cache_data # this lets the 
def load_geojson(url):
    geo_data = gpd.read_file(url)
    return geo_data

data_load_state = st.text('Loading data...')
geo_apl = load_geojson(GEO_URL)
data_load_state.text("") # change text from "Loading data..." to "" once the the load_data function has run

### TRANSFORM GEOJSON TO PANDAS
def geojson_to_dataframe(geo_apl):
    geo_apl = geo_apl.to_crs(epsg=4326)
    geo_apl_pd = geo_apl.drop(columns='geometry')
    return geo_apl_pd

### SIDEBAR
st.sidebar.header("Deserts medicaux")
st.sidebar.markdown("""
    * [Qu'est-ce qu'un desert medical ?](#qu-est-ce-qu-un-desert-medical)
    * [Pour mieux comprendre](#pour-mieux-comprendre)
    * [Comment les identifier ?](#comment-les-identifier)
    * [Quelques chiffres](#quelques-chiffres)
    * [Vivez-vous dans un desert medical ?](#vivez-vous-dans-un-desert-medical)

""")
e = st.sidebar.empty()
e.write("")
st.sidebar.write("Made with 💖 by Claudine, Jean-David et Alexandre")

### INTRODUCTION
st.header("Qu'est-ce qu'un desert medical ?")
st.markdown("""
    Un désert médical désigne une zone géographique où la population rencontre des difficultés pour accéder à des soins de santé. 
    La densité en professionnels ou établissements du secteur de la santé, en particulier en médecins, est, rapportée à sa population et ses besoins, nettement plus faible que dans le reste du pays.
""")

### VIDEO
st.header("Pour mieux comprendre")
with st.expander("⏯️ 85% des français vident dans un désert medical"):
    st.video("https://youtu.be/tuV_Av1MGAg?feature=shared")

st.markdown("---")

### APL def
st.header("Comment les identifier ?")
st.markdown("""
    Afin de pouvoir identifier ces deserts medicaux, l'etat a decidé de mettre en place un indicateur statistiques : l’APL (Accessibilité Potentielle Localisée).
    L'APL mesure l’adéquation spatiale entre l’offre et la demande de soins de premier recours. 
    En d'autres termes, il permet d’évaluer, pour chaque commune et pour une année précise, le niveau d’accès aux médecins généralistes de ses habitants.
""")

#### GRAPHS WITH TWO COLUMNS

st.header("Quelques chiffres")
col1, col2 = st.columns(2)

with col1:
    ### APL pies
    def plot_pie_chart(column_name, fig, row, col):
        # Count occurrences of each value in the specified column
        column_counts = geo_apl[column_name].value_counts().reset_index()
        column_counts.columns = [column_name, 'Count']
        
        # Define color mapping dictionary
        color_mapping = {
            "Commune carrencée (APL < 2.5)": "red",
            "Offre insuffisante (2.5 < APL < 4)": "orange",
            "Offre satisfaisante (APL > 4)": "green"
        }
        
        # Create the pie chart
        fig_pie = go.Pie(labels=column_counts[column_name], values=column_counts['Count'])
        fig_pie.marker.colors = [color_mapping.get(val, "") for val in column_counts[column_name]]
        
        # Add the pie chart to the specified subplot position
        fig.add_trace(fig_pie, row=row, col=col)

    def pie():
        st.markdown("Répartion des status APL")

        # Create a figure with three subplots arranged horizontally
        fig = make_subplots(rows=1, cols=3, specs=[[{'type':'pie'}, {'type':'pie'}, {'type':'pie'}]], horizontal_spacing=0.05, subplot_titles=("APL status (sans borne d'âge)", "APL status 65 et moins", "APL status 62 et moins"), row_titles=[""], shared_yaxes=False)

        # Plot each pie chart in its respective subplot
        plot_pie_chart("APL status (sans borne d'âge)", fig, 1, 1)
        plot_pie_chart("APL status 65 et moins", fig, 1, 2)
        plot_pie_chart("APL status 62 et moins", fig, 1, 3)

        # Update the layout to center the legend horizontally
        fig.update_layout(
            legend=dict(
                x=0.5,
                y=-0.1,
                xanchor='center',
                orientation="h"
            ), 
        )

        st.plotly_chart(fig, use_container_width=True)

    if __name__ == "__main__":
        pie()

with col2:
    ### APL map
    colors = [(0.0, 'red'),     # Red for values <= 0
            (0.25, 'orange'), # Orange for values between 0 and 2
            (0.75, 'yellow'), # Yellow for values between 2 and 3
            (1.0, 'white')]   # Green for values >= 4

    # Create the custom colormap
    custom_cmap = LinearSegmentedColormap.from_list('custom_cmap', colors)

    # Main function for Streamlit app
    def map(geo_apl):
        st.markdown("Carte des APLs")

        # Create a dropdown menu with the available columns
        column_dropdown = st.selectbox('Choisir une colonne :', options=["APL aux médecins généralistes (sans borne d'âge)", 
                                                                        "APL aux médecins généralistes de 65 ans et moins",
                                                                        "APL aux médecins généralistes de 62 ans et moins"])

        # Plot the data using GeoPandas
        fig, ax = plt.subplots()
        geo_apl.plot(column=column_dropdown, cmap=custom_cmap, legend=True, ax=ax, vmin=0, vmax=4, edgecolor='grey', linewidth=0.2)
        
        # Show a title
        ax.set_title(column_dropdown)
        
        # Remove axis
        ax.axis('off')
        
        # Show the map
        st.pyplot(fig, use_container_width=True)

    # Call the main function to run the Streamlit app
    if __name__ == "__main__":
        map(geo_apl)

### SHOW DATASET

# Transform GeoDataFrame to pandas DataFrame
geo_apl_pd = geojson_to_dataframe(geo_apl)
st.header("Vivez-vous dans un desert medical ?")

# Display dropdown menus for filters
selected_city = st.selectbox("Sélectionnez une ville :", [""] + list(geo_apl_pd["Ville"].unique()))
selected_department = st.selectbox("Sélectionnez un département :", [""] + list(geo_apl_pd["departement"].unique()))
selected_region = st.selectbox("Sélectionnez une région :", [""] + list(geo_apl_pd["region"].unique()))

# Add a button to reset filters
if st.button("Réinitialiser les filtres"):
    # Reset widget values
    selected_city = ""
    selected_department = ""
    selected_region = ""

# Filter the dataset based on selections
filtered_data = geo_apl_pd.copy()  # Copy the original dataset to avoid unexpected modifications

if selected_city:
    filtered_data = filtered_data[filtered_data["Ville"] == selected_city]

if selected_department:
    filtered_data = filtered_data[filtered_data["departement"] == selected_department]

if selected_region:
    filtered_data = filtered_data[filtered_data["region"] == selected_region]

# Display the filtered dataset
st.write(filtered_data)
