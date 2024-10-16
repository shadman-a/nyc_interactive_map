# NYC Interactive Map Project

This project visualizes various socioeconomic metrics and MTA ridership data across New York City ZIP codes on an interactive map.

## Project Overview

The project uses several data sources to create a detailed, interactive map of NYC that includes:
- Median household income
- Average commute time
- Population density
- Median property values
- MTA subway ridership

## Data Sources

1. NYC ZIP Code Shapefile - NYC Department of City Planning
2. Census Data (2022 ACS 5-Year Estimates) from data.census.gov:
   - Total Population (`population.csv`)
   - Average Commute Time (`commute_times.csv`)
   - Median Household Income (`median_income.csv`)
   - Median Property Value (`property_values.csv`)
3. MTA Ridership Data from NY Open Data

## Project Structure

```
nyc_interactive_map_project/
|
├── data/
│   ├── nyc_zip_code_0510.shp
│   ├── population.csv
│   ├── commute_times.csv
│   ├── median_income.csv
│   ├── property_values.csv
│   ├── ridership.csv
│   └── ridership_with_zip.csv
|
├── scripts/
│   ├── assign_zipcodes.py
│   └── interactive_map.py
|
├── venv/  (Virtual Environment folder)
|
└── interactive_map.html
```

## Setup and Usage

### Step 1: Set Up the Environment

1. Create Virtual Environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install Dependencies:
   ```
   pip install pandas geopandas folium shapely requests
   ```

### Step 2: Assign ZIP Codes to Ridership Data

Run the script to assign ZIP codes to the ridership data:

```
python scripts/assign_zipcodes.py
```

### Step 3: Generate the Interactive Map

Run the script to generate the interactive map:

```
python scripts/interactive_map.py
```

### Step 4: View the Map

Open `interactive_map.html` in your browser to view the map.

## Notes

- Ensure that all data files are placed in the `data/` folder before running the scripts.
- You need an active internet connection to install dependencies.

## License

This project is for educational purposes.
