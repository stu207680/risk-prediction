import matplotlib.pyplot as plot

import pandas as pd
import geopandas as geoPd

# ----------------------------------------------------------------------------------------------------
# global attribute(s):

FILE_PATH_DATA = "source code/risk-prediction/code/data/aisdk-2023-01/aisdk-"
data = ["2023-01-01", "2023-01-02"]

# ----------------------------------------------------------------------------------------------------

if __name__ == "__main__":
  for data_entry in data:
    geoDF = geoPd.GeoDataFrame((df := pd.read_csv(FILE_PATH_DATA + data_entry + ".csv")), geometry = geoPd.points_from_xy(df.Latitude, df.Longitude))
    print(df.head(8))
    geoDF.plot(figsize = (12, 12), markersize = 0.8, alpha = 0.8)
    plot.savefig("AIS_" + data_entry + ".jpg")