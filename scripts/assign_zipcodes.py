# assign_zipcodes.py

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Load NYC ZIP Code shapefile
geo_gdf = gpd.read_file('/Users/shadman/nyc_interactive_map/data/nyc_zip_code_0510.shp')

# Set the CRS of the shapefile to EPSG:4326 (or another appropriate CRS)
geo_gdf.set_crs(epsg=4326, inplace=True)

# Use the 'zcta' column to represent ZIP codes
geo_gdf['zcta'] = geo_gdf['zcta'].astype(str)

# Load Ridership Data with Latitude and Longitude
ridership_df = pd.read_csv('/Users/shadman/nyc_interactive_map/data/ridership.csv', low_memory=False)

# Assuming your ridership data has 'latitude' and 'longitude' columns
geometry = [Point(xy) for xy in zip(ridership_df['longitude'], ridership_df['latitude'])]
ridership_gdf = gpd.GeoDataFrame(ridership_df, geometry=geometry)
ridership_gdf.crs = "EPSG:4326"  # Set CRS to WGS84 (latitude and longitude)

# Perform spatial join to assign ZIP codes to each station based on location
ridership_with_zip = gpd.sjoin(ridership_gdf, geo_gdf, how="left", predicate="intersects")

# Select relevant columns
ridership_with_zip = ridership_with_zip[['station_complex_id', 'latitude', 'longitude', 'ridership', 'zcta']]

# Rename the ZIP Code column
ridership_with_zip.rename(columns={'zcta': 'zip_code'}, inplace=True)

# Save the updated ridership data to CSV
ridership_with_zip.to_csv('/Users/shadman/nyc_interactive_map/data/ridership_with_zip.csv', index=False)

print("Ridership data with ZIP codes saved to 'data/ridership_with_zip.csv'")
