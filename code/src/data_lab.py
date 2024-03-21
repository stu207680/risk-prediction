import matplotlib.pyplot as plot

import pandas as pd
import geopandas as geoPd
import movingpandas as movePd
import warnings

from datetime import timedelta

# ----------------------------------------------------------------------------------------------------
# global attribute(s):

FILE_PATH_DATA = "source code/risk-prediction/code/data/aisdk-2023-01/aisdk-"
data_files = ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05", "2023-01-06", "2023-01-07", "2023-01-08", "2023-01-09", "2023-01-10"]

SET_OF_COLORS = {"Cargo": "orange", "HSC": "green", "Passenger": "blue", "Tanker": "red", "Diving":"grey", "Dredging": "grey", "Fishing": "grey", "Law enforcement": "grey", "Military": "grey", "Other": "grey", "Pilot": "grey", "Pleasure": "grey", "Port tender": "grey", "Reserved": "grey", "SAR": "grey", "Sailing": "grey", "Spare 2": "grey", "Towing": "grey", "Tug": "grey", "Undefined": "grey"}

# ----------------------------------------------------------------------------------------------------

if __name__ == "__main__":
  warnings.filterwarnings("ignore")
  for data_entry in data_files:
    df = pd.read_csv(FILE_PATH_DATA + data_entry + ".csv")
    df = df.drop(["Type of mobile", "Heading", "IMO", "Callsign", "Width", "Length", "Type of position fixing device", "Draught", "Destination", "ETA", "Data source type", "A", "B", "C", "D"], axis = 1)
    # df = df.reset_index()
    df = df.rename(columns = {"# Timestamp": "Timestamp"})
    df = df.drop_duplicates(subset = ["Timestamp"])
    # df.set_index()
    geoDF = geoPd.GeoDataFrame(df, geometry = geoPd.points_from_xy(df.Latitude, df.Longitude))
    geoDF.to_file(FILE_PATH_DATA + data_entry + ".gpkg", driver = "GPKG")
    data = geoPd.read_file(FILE_PATH_DATA + data_entry + ".gpkg")
    data = data[data.SOG > 0.0].copy()
    print("--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    print(data.head())
    print(data.shape)
    print("--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    data["TIME"] = pd.to_datetime(data["Timestamp"], format = "%d/%m/%Y %H:%M:%S")
    data = data.set_index("TIME")
    data.plot(figsize = (12, 12), markersize = 0.8, alpha = 0.8)
    plot.savefig(FILE_PATH_DATA + data_entry + ".jpg")
    collection = movePd.TrajectoryCollection(data, "MMSI", min_length = 100)
    collection = movePd.MinTimeDeltaGeneralizer(collection).generalize(tolerance = timedelta(minutes = 1))
    collection.plot(column = "Ship type", column_to_color = SET_OF_COLORS, linewidth = 1, capstyle = "round")
    for trajectory in collection.trajectories:
      print(trajectory.df.head())
      trajectory.hvplot(title = f"trajectory: {trajectory.id}", frame_width = 1024, frame_height = 720, line_width = 5.0, cmap = "Dark2")