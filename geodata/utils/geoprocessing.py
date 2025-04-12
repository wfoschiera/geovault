import json
import os

import geopandas as gpd
import pandas as pd


def convert_raw_to_geojson(file_path):
    """
    Process various geographic file formats into GeoJSON

    Args:
        file_path: Path to the uploaded file

    Returns:
        dict: A dictionary containing geometry and properties
    """
    extension = os.path.splitext(file_path)[1].lower()

    try:
        if extension in [".shp", ".gpkg", ".geojson", ".kml"]:
            # Read the file using GeoPandas
            gdf = gpd.read_file(file_path)

            # Ensure the CRS is WGS84 (EPSG:4326)
            if gdf.crs and gdf.crs != "EPSG:4326":
                gdf = gdf.to_crs("EPSG:4326")

            # Convert to GeoJSON
            geojson_str = gdf.to_json()
            geojson_data = json.loads(geojson_str)

            return geojson_data

        elif extension in [".csv", ".xlsx"]:
            # Assuming CSV or Excel has latitude and longitude columns
            if extension == ".csv":
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            # Check if the required columns exist
            required_cols = ["latitude", "longitude"]
            if not all(col.lower() in map(str.lower, df.columns) for col in required_cols):
                raise ValueError("CSV/Excel must contain latitude and longitude columns")

            # Create GeoDataFrame
            lat_col = [col for col in df.columns if col.lower() == "latitude"][0]
            lng_col = [col for col in df.columns if col.lower() == "longitude"][0]

            gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df[lng_col], df[lat_col]), crs="EPSG:4326")

            # Convert to GeoJSON
            geojson_str = gdf.to_json()
            geojson_data = json.loads(geojson_str)

            return geojson_data

        else:
            raise ValueError(f"Unsupported file extension: {extension}")

    except Exception as e:
        raise ValueError(f"Error processing file: {str(e)}")
