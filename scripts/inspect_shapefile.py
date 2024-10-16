# inspect_shapefile.py

import geopandas as gpd

# Load the NYC ZIP Code shapefile
geo_gdf = gpd.read_file('/Users/shadman/nyc_interactive_map/data/nyc_zip_code_0510.shp')

# Print the column names
print(geo_gdf.columns)
