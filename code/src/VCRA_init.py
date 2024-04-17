from os.path import exists

import cri_helper
import encounters
import st_toolkit

import geopandas as geoPd
import pandas as pd
import tqdm

DEFAULT_FILE_PATH = f"source code/risk-prediction/code/data/unipi_ais_dynamic_2017/"
FILE_HANDLER = f"unipi_ais_dynamic_aug2017.csv"

GEODATA_FILE_PATH = f"source code/risk-prediction/code/data/geodata/harbours/"

if not exists(f"source code/risk-prediction/code/result(s)/geoDataframe.pickle"):
  geoDataframe = geoPd.GeoDataFrame(dataframe := pd.read_csv(DEFAULT_FILE_PATH + FILE_HANDLER).sort_values(by = ["t"]).drop_duplicates(subset = ["t", "vessel_id"], keep = "first"), crs = 4326, geometry = geoPd.points_from_xy(dataframe["lon"], dataframe["lat"]))
  geoDataframe.rename({"vessel_id": "mmsi"}, axis = 1, inplace = True)
  geoDataframe.rename({"t": "timestamp"}, axis = 1, inplace = True)
  geoDataframe["datetime"] = pd.to_datetime(geoDataframe["timestamp"], unit = "ms")
  geoDataframe["timestamp"] = geoDataframe["timestamp"] / 10**3

  # CLASSIFY AREA PROXIMITY:
  tqdm.tqdm.pandas()
  geoDataframe = st_toolkit.classify_area_proximity(geoDataframe.copy(), geoPd.read_file(GEODATA_FILE_PATH), o_id_column = "mmsi", ts_column = "timestamp", area_radius = 1852, area_epsg = 2100)
  geoDataframe = geoDataframe.drop("traj_id", axis = 1).sort_values("timestamp").groupby("mmsi", group_keys = False).progress_apply(lambda df: st_toolkit.spatial_segmentation(df, col_name = "label", threshold = 1, output_name = "spat_traj_nr", min_pts = 10))

  # TEMPORAL SEGMENTATION:
  tqdm.tqdm.pandas()
  geoDataframe = geoDataframe.sort_values("timestamp").groupby(["mmsi", "spat_traj_nr"], group_keys = False).progress_apply(lambda df: st_toolkit.temporal_segmentation(df.copy(), **dict(col_name = "timestamp", threshold = 30 * 60 + 1e-9, min_pts = 10, output_name = "temp_traj_nr")))
  geoDataframe.loc[:, "traj_nr"] = geoDataframe.groupby(["mmsi", "spat_traj_nr", "temp_traj_nr"]).ngroup()

  # TEMPORAL ALIGNMENT:
  tqdm.tqdm.pandas()
  geoDataframe = geoDataframe.groupby(["mmsi", "traj_nr"]).progress_apply(lambda df: st_toolkit.temporal_resampling_v2(df.copy(), **dict(features = ["timestamp", 'lon', 'lat', "speed", "course"], o_id_name = "mmsi", temporal_name = "datetime", temporal_unit = "s", rate = "30s", method = "linear", min_pts = 4)))
  geoDataframe = geoDataframe.drop("mmsi", axis = 1).reset_index().drop("level_2", axis = 1)
  geoDataframe = geoPd.GeoDataFrame(geoDataframe, crs = 4326, geometry = geoPd.points_from_xy(geoDataframe["lon"], geoDataframe["lat"]))
  geoDataframe.sort_values("timestamp", ascending = True, inplace = True)
  geoDataframe = st_toolkit.add_speed(geoDataframe, o_id = ["mmsi", "traj_nr"], ts = "timestamp", speed = "speed", geometry = "geometry")
  geoDataframe = st_toolkit.add_course(geoDataframe, o_id = ["mmsi", "traj_nr"], ts = "timestamp", course = "course", geometry = "geometry")
  geoDataframe["length"] = 100
  geoDataframe.to_pickle(f"source code/risk-prediction/code/result(s)/geoDataframe.pickle")
else:
  geoDataframe = pd.read_pickle(f"source code/risk-prediction/code/result(s)/geoDataframe.pickle")
if not (exists(f"source code/risk-prediction/code/result(s)/encountering_pair.pickle") or exists(f"source code/risk-prediction/code/result(s)/encountering_result.pickle")):
  encountering_pair, result = encounters.encountering_vessels(geoDataframe, dt_name = "datetime")
  encountering_pair.to_pickle(f"source code/risk-prediction/code/result(s)/encountering_pair.pickle")
  cri_helper.homogenize_units(result.copy()).to_pickle(f"source code/risk-prediction/code/result(s)/encountering_result.pickle")
else:
  encountering_pair = pd.read_pickle(f"source code/risk-prediction/code/result(s)/encountering_pair.pickle")
  result = pd.read_pickle(f"source code/risk-prediction/code/result(s)/encountering_result.pickle")
pass