import algorithms.ARSC_FC.utils.calculations.STT

import geopandas as geoPd
import glob
import numpy as np
import pandas as pd
import tqdm

GEO_DATA_FILE_PATH = f"source_code/risk-prediction/code/data/data/.csv/geodata/harbours" 

def model_builder(file_paths):
  dataframe = pd.DataFrame()
  for file_path in file_paths:
    files = glob.glob(file_path + "/*.csv")
    for file in files:
      dataframe = pd.concat([dataframe, pd.read_csv(file)])
  dataframe = dataframe.sort_values(by = ["t"]).drop_duplicates(subset = ["t", "vessel_id"], keep = "first")
  geoDataframe = geoPd.GeoDataFrame(dataframe, crs = 4326, geometry = geoPd.points_from_xy(dataframe["lon"], dataframe["lat"]))
  geoDataframe.rename({"vessel_id": "mmsi"}, axis = 1, inplace = True)
  geoDataframe.rename({"t": "timestamp"}, axis = 1, inplace = True)
  geoDataframe["datetime"] = pd.to_datetime(geoDataframe["timestamp"], unit = "ms")
  geoDataframe["timestamp"] = geoDataframe["timestamp"] / 10**3

  # geoDataframe = algorithms.ARSC_FC.utils.calculations.STT.add_speed(geoDataframe, o_id = ["mmsi", "traj_nr"], ts = "timestamp", speed = "speed", geometry = "geometry")
  # geoDataframe = geoDataframe.loc[geoDataframe.speed <= 50].copy()

  # CLASSIFY AREA PROXIMITY:
  tqdm.tqdm.pandas()
  geoDataframe = algorithms.ARSC_FC.utils.calculations.STT.classify_area_proximity(geoDataframe.copy(), geoPd.read_file(GEO_DATA_FILE_PATH), o_id_column = "mmsi", ts_column = "timestamp", area_radius = 1852, area_epsg = 2100)
  geoDataframe = geoDataframe.drop("traj_id", axis = 1).sort_values("timestamp").groupby("mmsi", group_keys = False).progress_apply(lambda df: algorithms.ARSC_FC.utils.calculations.STT.spatial_segmentation(df, col_name = "label", threshold = 1, output_name = "spat_traj_nr", min_pts = 10))

  # TEMPORAL SEGMENTATION:
  tqdm.tqdm.pandas()
  geoDataframe = geoDataframe.sort_values("timestamp").groupby(["mmsi", "spat_traj_nr"], group_keys = False).progress_apply(lambda df: algorithms.ARSC_FC.utils.calculations.STT.temporal_segmentation(df.copy(), **dict(col_name = "timestamp", threshold = 30 * 60 + 1e-9, min_pts = 10, output_name = "temp_traj_nr")))
  geoDataframe.loc[:, "traj_nr"] = geoDataframe.groupby(["mmsi", "spat_traj_nr", "temp_traj_nr"]).ngroup()

  # TEMPORAL ALIGNMENT:
  tqdm.tqdm.pandas()
  geoDataframe = geoDataframe.groupby(["mmsi", "traj_nr"]).progress_apply(lambda df: algorithms.ARSC_FC.utils.calculations.STT.temporal_resampling_v2(df.copy(), **dict(features = ["timestamp", 'lon', 'lat', "speed", "course"], o_id_name = "mmsi", temporal_name = "datetime", temporal_unit = "s", rate = "30s", method = "linear", min_pts = 4)))
  geoDataframe = geoDataframe.drop("mmsi", axis = 1).reset_index().drop("level_2", axis = 1)
  geoDataframe = geoPd.GeoDataFrame(geoDataframe, crs = 4326, geometry = geoPd.points_from_xy(geoDataframe["lon"], geoDataframe["lat"]))
  geoDataframe.sort_values("timestamp", ascending = True, inplace = True)
  geoDataframe = algorithms.ARSC_FC.utils.calculations.STT.add_speed(geoDataframe, o_id = ["mmsi", "traj_nr"], ts = "timestamp", speed = "speed", geometry = "geometry")
  geoDataframe = algorithms.ARSC_FC.utils.calculations.STT.add_course(geoDataframe, o_id = ["mmsi", "traj_nr"], ts = "timestamp", course = "course", geometry = "geometry")
  geoDataframe["length"] = 100

  geoDataframe.insert(geoDataframe.columns.get_loc("course") + 1, "course_rad", geoDataframe.course.apply(lambda x: np.deg2rad(x)))

  geoDataframe.to_pickle(f"source_code/risk-prediction/code/data/.ML_model/geoDataframe.pickle")
  return geoDataframe