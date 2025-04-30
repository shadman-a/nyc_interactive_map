# interactive_map_enhanced.py

import pandas as pd
import geopandas as gpd
import folium
from folium.features import GeoJsonPopup, GeoJsonTooltip
from branca.colormap import LinearColormap
from folium.plugins import MarkerCluster, MiniMap, Search
import matplotlib.pyplot as plt
import seaborn as sns

# -----------------------------
# Data Loading and Preprocessing
# -----------------------------

# Load NYC ZIP Code shapefile
geo_gdf = gpd.read_file('/Users/shadman/nyc_interactive_map/data/nyc_zip_code_0510.shp')
geo_gdf['zcta'] = geo_gdf['zcta'].astype(str)

# Load Median Income Data
income_df = pd.read_csv('/Users/shadman/nyc_interactive_map/data/median_income.csv')
income_df['zip_code'] = income_df['GEO_ID'].str[-5:]
income_df = income_df[['zip_code', 'B19013_001E']]
income_df.rename(columns={'B19013_001E': 'median_income'}, inplace=True)
income_df['zip_code'] = income_df['zip_code'].astype(str)

# Load Average Commute Time Data
commute_df = pd.read_csv('/Users/shadman/nyc_interactive_map/data/commute_times.csv')
commute_df['zip_code'] = commute_df['GEO_ID'].str[-5:]
commute_df = commute_df[['zip_code', 'B08303_001E']]
commute_df.rename(columns={'B08303_001E': 'average_commute_time'}, inplace=True)
commute_df['zip_code'] = commute_df['zip_code'].astype(str)

# Load Population Data
population_df = pd.read_csv('/Users/shadman/nyc_interactive_map/data/population.csv')
population_df['zip_code'] = population_df['GEO_ID'].str[-5:]
population_df = population_df[['zip_code', 'B01003_001E']]
population_df.rename(columns={'B01003_001E': 'total_population'}, inplace=True)
population_df['zip_code'] = population_df['zip_code'].astype(str)

# Load Median Property Value Data
property_df = pd.read_csv('/Users/shadman/nyc_interactive_map/data/property_values.csv')
property_df['zip_code'] = property_df['GEO_ID'].str[-5:]
property_df = property_df[['zip_code', 'B25077_001E']]
property_df.rename(columns={'B25077_001E': 'median_property_value'}, inplace=True)
property_df['zip_code'] = property_df['zip_code'].astype(str)

# Load Ridership Data with ZIP Codes
ridership_df = pd.read_csv('/Users/shadman/nyc_interactive_map/data/ridership_with_zip.csv', low_memory=False)
ridership_df['zip_code'] = ridership_df['zip_code'].astype(str)

# Group by ZIP code and aggregate ridership
ridership_by_zip = ridership_df.groupby('zip_code').agg({'ridership': 'sum'}).reset_index()

# Merge datasets
geo_merged = geo_gdf.merge(income_df, left_on='zcta', right_on='zip_code', how='left')
geo_merged = geo_merged.merge(commute_df, on='zip_code', how='left')
geo_merged = geo_merged.merge(population_df, on='zip_code', how='left')
geo_merged = geo_merged.merge(property_df, on='zip_code', how='left')
geo_merged = geo_merged.merge(ridership_by_zip, left_on='zcta', right_on='zip_code', how='left')

# Drop rows with missing geometry
geo_merged = geo_merged.dropna(subset=['geometry'])

# Convert necessary columns to numeric types
numeric_columns = ['median_income', 'average_commute_time', 'total_population',
                   'median_property_value', 'ridership']
for col in numeric_columns:
    geo_merged[col] = pd.to_numeric(geo_merged[col], errors='coerce')

# Set CRS for geo_merged before transforming
geo_merged.set_crs(epsg=4326, inplace=True)

# Calculate Population Density
geo_merged = geo_merged.to_crs(epsg=32618)
geo_merged['area_sq_miles'] = geo_merged['geometry'].area / 2.59e+6  # Convert from square meters to square miles
geo_merged['population_density'] = geo_merged['total_population'] / geo_merged['area_sq_miles']

# Convert back to WGS84 for mapping
geo_merged = geo_merged.to_crs(epsg=4326)

# Create copies of numeric columns before formatting for tooltips
geo_merged['median_income_numeric'] = geo_merged['median_income']
geo_merged['median_property_value_numeric'] = geo_merged['median_property_value']
geo_merged['ridership_numeric'] = geo_merged['ridership']
geo_merged['average_commute_time_numeric'] = geo_merged['average_commute_time']
geo_merged['population_density_numeric'] = geo_merged['population_density']

# Format numeric fields for better readability in tooltips
geo_merged['median_income'] = geo_merged['median_income'].apply(lambda x: f"${x:,.0f}" if pd.notnull(x) else "N/A")
geo_merged['median_property_value'] = geo_merged['median_property_value'].apply(lambda x: f"${x:,.0f}" if pd.notnull(x) else "N/A")
geo_merged['ridership'] = geo_merged['ridership'].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "N/A")
geo_merged['population_density'] = geo_merged['population_density'].apply(lambda x: f"{x:,.1f}" if pd.notnull(x) else "N/A")
geo_merged['average_commute_time'] = geo_merged['average_commute_time'].apply(lambda x: f"{x:.1f}" if pd.notnull(x) else "N/A")

# -----------------------------
# Map Creation and Enhancements
# -----------------------------

# Initialize the map with a custom tile
m = folium.Map(
    location=[40.7128, -74.0060],
    zoom_start=11,
    tiles='Stamen Toner Lite',
    attr='Stamen Toner Lite'
)

# Define color scales using colorblind-friendly palettes
color_scales = {
    'Median Income': LinearColormap(
        ['#f7fbff', '#08306b'],
        vmin=geo_merged['median_income_numeric'].min(),
        vmax=geo_merged['median_income_numeric'].max()
    ),
    'Average Commute Time': LinearColormap(
        ['#fff7ec', '#7f0000'],
        vmin=geo_merged['average_commute_time_numeric'].min(),
        vmax=geo_merged['average_commute_time_numeric'].max()
    ),
    'Population Density': LinearColormap(
        ['#ffffcc', '#006837'],
        vmin=geo_merged['population_density_numeric'].min(),
        vmax=geo_merged['population_density_numeric'].max()
    ),
    'Median Property Value': LinearColormap(
        ['#f7fcf5', '#00441b'],
        vmin=geo_merged['median_property_value_numeric'].min(),
        vmax=geo_merged['median_property_value_numeric'].max()
    ),
    'Ridership': LinearColormap(
        ['#fff5f0', '#67000d'],
        vmin=geo_merged['ridership_numeric'].min(),
        vmax=geo_merged['ridership_numeric'].max()
    )
}

# Create style_function and highlight_function
def create_style_function(data_col_numeric, color_scale):
    return lambda feature: {
        'fillColor': color_scale(feature['properties'][data_col_numeric]) if feature['properties'][data_col_numeric] is not None else 'transparent',
        'color': 'gray',
        'weight': 0.5,
        'fillOpacity': 0.6 if feature['properties'][data_col_numeric] is not None else 0,
    }

def create_highlight_function():
    return lambda feature: {
        'fillColor': '#ffffbf',
        'color': 'black',
        'weight': 2,
        'fillOpacity': 0.9,
    }

# Function to create choropleth layers with pop-ups
def add_choropleth_with_popup(gdf, data_col_numeric, name, color_scale, legend_name):
    style_function = create_style_function(data_col_numeric, color_scale)
    highlight_function = create_highlight_function()

    # Define the fields and aliases for the pop-up
    popup_fields = ['zcta', 'median_income', 'average_commute_time', 'population_density',
                    'median_property_value', 'ridership']
    popup_aliases = ['ZIP Code:', 'Median Income:', 'Average Commute Time (mins):',
                     'Population Density (people/sq mile):', 'Median Property Value:', 'Total Ridership:']

    # Create the GeoJson layer
    geojson = folium.GeoJson(
        data=gdf,
        style_function=style_function,
        highlight_function=highlight_function,
        name=name,
        tooltip=folium.GeoJsonTooltip(
            fields=['zcta'],
            aliases=['ZIP Code:'],
            localize=True
        ),
        popup=folium.GeoJsonPopup(
            fields=popup_fields,
            aliases=popup_aliases,
            localize=True,
            labels=True,
            style="""
                background-color: #FFFFFF;
                border: 1px solid black;
                border-radius: 3px;
                padding: 10px;
            """,
            max_width=300
        ),
    )

    color_scale.caption = legend_name
    m.add_child(geojson)
    m.add_child(color_scale)

# Prepare the data for each layer
layer_columns = ['geometry', 'zcta', 'median_income', 'median_income_numeric', 'average_commute_time',
                 'average_commute_time_numeric', 'population_density', 'population_density_numeric',
                 'median_property_value', 'median_property_value_numeric', 'ridership', 'ridership_numeric']

# Add the choropleth layers
add_choropleth_with_popup(
    geo_merged[layer_columns],
    'median_income_numeric',
    'Median Income',
    color_scales['Median Income'],
    'Median Income ($)'
)

add_choropleth_with_popup(
    geo_merged[layer_columns],
    'average_commute_time_numeric',
    'Average Commute Time',
    color_scales['Average Commute Time'],
    'Average Commute Time (mins)'
)

add_choropleth_with_popup(
    geo_merged[layer_columns],
    'population_density_numeric',
    'Population Density',
    color_scales['Population Density'],
    'Population Density (people per sq mile)'
)

add_choropleth_with_popup(
    geo_merged[layer_columns],
    'median_property_value_numeric',
    'Median Property Value',
    color_scales['Median Property Value'],
    'Median Property Value ($)'
)

add_choropleth_with_popup(
    geo_merged[layer_columns],
    'ridership_numeric',
    'Ridership',
    color_scales['Ridership'],
    'Total Ridership'
)

# -----------------------------
# Adding Subway Data
# -----------------------------

# Load and add subway data
subway_lines = gpd.read_file('/Users/shadman/nyc_interactive_map/data/nyc_subway_lines.geojson')
subway_lines.to_crs(epsg=4326, inplace=True)

subway_stations = gpd.read_file('/Users/shadman/nyc_interactive_map/data/nyc_subway_stations.geojson')
subway_stations.to_crs(epsg=4326, inplace=True)

# Style subway lines
def style_subway_lines(feature):
    return {
        'color': 'blue',
        'weight': 2,
        'opacity': 0.7,
    }

# Add subway lines
folium.GeoJson(
    subway_lines,
    style_function=style_subway_lines,
    name='Subway Lines'
).add_to(m)

# Use marker clustering for subway stations
marker_cluster = MarkerCluster(name='Subway Stations').add_to(m)
for idx, row in subway_stations.iterrows():
    station_name = row['description']  # Use 'description' field
    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],
        radius=4,
        color='red',
        fill=True,
        fill_color='red',
        fill_opacity=0.7,
        popup=folium.Popup(f"Station: {station_name}", max_width=200),
    ).add_to(marker_cluster)

# -----------------------------
# Adding Additional Features
# -----------------------------

# Add search functionality
geojson_layer = folium.GeoJson(
    geo_merged[['geometry', 'zcta']],
    name='Search Layer',
    style_function=lambda feature: {
        'color': 'transparent',
        'fillColor': 'transparent',
        'fillOpacity': 0
    }
)

search = Search(
    layer=geojson_layer,
    geom_type='Polygon',
    placeholder='Search for ZIP Code',
    search_label='zcta',
    collapsed=False,
    position='topright'
).add_to(m)

m.add_child(geojson_layer)

# Add minimap
minimap = MiniMap(toggle_display=True, position='bottomright')
m.add_child(minimap)

# Add layer control to toggle between choropleth layers and subway layers
folium.LayerControl(collapsed=False).add_to(m)

# Ensure mobile responsiveness
m.get_root().html.add_child(folium.Element('''
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
'''))

# -----------------------------
# Statistical Analysis (Optional)
# -----------------------------

# Uncomment the following code if you wish to perform statistical analysis

# metrics = ['median_income_numeric', 'average_commute_time_numeric', 'population_density_numeric',
#            'median_property_value_numeric', 'ridership_numeric']

# # Summary Statistics
# summary_stats = geo_merged[metrics].describe()
# print("Summary Statistics:")
# print(summary_stats)

# # Correlation Matrix
# correlation_matrix = geo_merged[metrics].corr()
# print("Correlation Matrix:")
# print(correlation_matrix)

# # Plot correlation heatmap
# plt.figure(figsize=(10, 8))
# sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
# plt.title('Correlation Heatmap of Socio-Economic Indicators')
# plt.tight_layout()
# plt.show()

# -----------------------------
# Save the Map
# -----------------------------

# Save the map
m.save('/Users/shadman/nyc_interactive_map/interactive_map_enhanced.html')

print("Enhanced interactive map saved to 'interactive_map_enhanced.html'")
