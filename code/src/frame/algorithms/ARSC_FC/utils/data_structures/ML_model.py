from joblib import Parallel, delayed
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_squared_log_error
from sklearn.model_selection import StratifiedKFold
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

import numpy as np
import pandas as pd
import tqdm
import warnings

"""
purpose: Common interface for the machine learning model for the Advanced Route Skyline Computation algorithm family.\n
"""
class ML_MODEL:
  """
  purpose: Create a machine learning model.\n
  I/O:
    - input: @storage stores the machine learning model.
             @ML_data contains the data for training.
    - output: Returns a machine learning model.
  """
  def create_ML_model(self, storage, ML_data):
    warnings.simplefilter(action = "ignore", category = FutureWarning)

    # hidden short-hand function for running a machine learning model.
    def run_ML_model(X, y, binned_y):
      # hidden short-hand function for machine learning model training.
      def training_ML_model(model, X, y, train_index, test_index):
        X_train, X_test = X.iloc[train_index].values, X.iloc[test_index].values
        y_train, y_test = y.iloc[train_index].values, y.iloc[test_index].values
        model.fit(X_train, y_train)
        y_pred = np.clip(model.predict(X_test), 0, 1)
        return dict(instance = model, train_indices = train_index, test_indices = test_index, y_true = y_test, y_pred = y_pred, acc = model.score(X_test, y_test), mae = mean_absolute_error(y_test, y_pred), rmse = mean_squared_error(y_test, y_pred, squared = False), rmsle = mean_squared_log_error(y_test, y_pred, squared = False))

      training_data = X.loc[:, ["own_speed", "own_course_rad", "target_speed", "target_course_rad", "dist_euclid", "azimuth_angle_target_to_own", "rel_movement_direction"]].copy()
      sKF = StratifiedKFold(n_splits = 5, shuffle = True, random_state = 10)
      model = make_pipeline(StandardScaler(), MLPRegressor(random_state = 10, max_iter = 300, hidden_layer_sizes = (256, 32), verbose = False, early_stopping = True, n_iter_no_change = 7))
      result_dataframe = pd.DataFrame(Parallel(n_jobs = -1)(delayed(training_ML_model)(model, training_data, y, train_index, test_index) for (train_index, test_index) in tqdm.tqdm(sKF.split(X, binned_y), total = sKF.get_n_splits(X, y))))
      return result_dataframe["instance"].loc[result_dataframe["acc"].idxmax()]

    ML_data.loc[:, "ves_cri_bin"] = pd.cut(ML_data.ves_cri, bins = np.arange(0, 1.1, .2), right = True, include_lowest = True)
    X, y, y_bin = ML_data.iloc[:, :-2], ML_data.iloc[:, -2], ML_data.iloc[:, -1].astype("str")
    return run_ML_model(X = X, y = y, binned_y = y_bin)