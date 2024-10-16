# interactive_map.py

import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import MarkerCluster
from branca.element import Template, MacroElement

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
geo_merged['median_income'] = pd.to_numeric(geo_merged['median_income'], errors='coerce')
geo_merged['average_commute_time'] = pd.to_numeric(geo_merged['average_commute_time'], errors='coerce')
geo_merged['total_population'] = pd.to_numeric(geo_merged['total_population'], errors='coerce')
geo_merged['median_property_value'] = pd.to_numeric(geo_merged['median_property_value'], errors='coerce')
geo_merged['ridership'] = pd.to_numeric(geo_merged['ridership'], errors='coerce')

# Set CRS for geo_merged before transforming
geo_merged.set_crs(epsg=4326, inplace=True)

# Calculate Population Density
geo_merged = geo_merged.to_crs(epsg=32618)
geo_merged['area_sq_miles'] = geo_merged['geometry'].area / 2.59e+6
geo_merged['population_density'] = geo_merged['total_population'] / geo_merged['area_sq_miles']

# Convert back to WGS84 for mapping
geo_merged = geo_merged.to_crs(epsg=4326)

# Initialize the map centered on NYC
m = folium.Map(location=[40.7128, -74.0060], zoom_start=11)

# Function to create choropleth layers
def add_choropleth(geo_data, data, name, columns, key_on, fill_color, legend_name):
    choropleth = folium.Choropleth(
        geo_data=geo_data,
        data=data,
        columns=columns,
        key_on=key_on,
        fill_color=fill_color,
        fill_opacity=0.7,
        line_opacity=0.2,
        nan_fill_color='white',
        nan_fill_opacity=0.4,
        highlight=True,
        name=name,
        legend_name=legend_name
    )
    choropleth.add_to(m)
    return choropleth

# Add choropleth layers
add_choropleth(geo_merged, geo_merged, 'Median Income', ['zcta', 'median_income'], 'feature.properties.zcta', 'YlGn', 'Median Income ($)')
add_choropleth(geo_merged, geo_merged, 'Average Commute Time', ['zcta', 'average_commute_time'], 'feature.properties.zcta', 'PuBu', 'Average Commute Time (mins)')
add_choropleth(geo_merged, geo_merged, 'Population Density', ['zcta', 'population_density'], 'feature.properties.zcta', 'OrRd', 'Population Density (people per sq mile)')
add_choropleth(geo_merged, geo_merged, 'Median Property Value', ['zcta', 'median_property_value'], 'feature.properties.zcta', 'YlOrBr', 'Median Property Value ($)')
add_choropleth(geo_merged, geo_merged, 'Ridership', ['zcta', 'ridership'], 'feature.properties.zcta', 'BuGn', 'Total Ridership')

# Add layer control to toggle between choropleth layers
folium.LayerControl(collapsed=False).add_to(m)

# Save the map
m.save('/Users/shadman/nyc_interactive_map/interactive_map.html')

print("Interactive map saved to 'interactive_map.html'")
