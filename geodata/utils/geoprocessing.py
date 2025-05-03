import json
import os
from datetime import datetime

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


def apply_dummy_operation(geojson_data, operation, param=None):
    """
    Apply a dummy operation to simulate data processing on a GeoJSON object

    Args:
        geojson_data: GeoJSON data (as dictionary)
        operation: The operation to perform (simplify, buffer, etc.)
        param: Optional parameter for the operation

    Returns:
        dict: Processed GeoJSON data
    """
    try:
        # Convert the geojson back to a GeoDataFrame
        gdf = gpd.GeoDataFrame.from_features(geojson_data["features"])

        # Apply the dummy operation
        if operation == "simplify":
            # Simulate simplifying geometries (reducing complexity)
            tolerance = param or 0.001
            gdf["geometry"] = gdf["geometry"].simplify(tolerance)

        elif operation == "buffer":
            # Simulate buffering features
            distance = param or 0.01  # degrees
            gdf["geometry"] = gdf["geometry"].buffer(distance)

        elif operation == "reproject":
            # Just a dummy operation that doesn't actually change projection
            gdf["geometry"] = gdf["geometry"]
            # In a real operation, you might do:
            # gdf = gdf.to_crs(new_crs)

        elif operation == "extract":
            # Dummy operation to simulate extracting only certain properties
            # Just returns the original data in this example
            pass

        # Add a property to indicate processing was done
        for i in range(len(gdf)):
            if "properties" not in gdf.iloc[i] or gdf.iloc[i]["properties"] is None:
                gdf.iloc[i]["properties"] = {}
            props = gdf.iloc[i]["properties"]
            props["processed_with"] = operation
            props["process_param"] = str(param) if param is not None else "default"
            props["process_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Convert back to GeoJSON
        result = json.loads(gdf.to_json())
        return result

    except Exception as e:
        raise ValueError(f"Error applying operation: {str(e)}")
