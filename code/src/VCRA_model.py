from joblib import Parallel, delayed

from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_squared_log_error
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

import argparse
import numpy as np
import pandas as pd
pd.set_option("display.max_columns", None)
import tqdm
import warnings
warnings.simplefilter(action = "ignore", category = FutureWarning)

def evaluate_clf(clf, X, y, train_index, test_index, include_indices = False):
  print(f"Training with {len(train_index)} samples.")
  print(f"Testing with {len(test_index)} samples.")

  X_train, X_test = X.iloc[train_index].values, X.iloc[test_index].values
  y_train, y_test = y.iloc[train_index].values, y.iloc[test_index].values
  # call regr.predict(...): X_train: own_speed X, own_course_rad (X), target_speed X, target_course_rad X, dist_euclid X: (st_toolkit.py: haversine), azimuth_angle_target_to_own X: (cri_calc.py: calculate_cpa), rel_movement_direction X: (cri_calc.py: calculate_cpa) -> ves_cri
  clf.fit(X_train, y_train)
  # IMPORTANT STEP!
  y_pred = np.clip(clf.predict(X_test), 0, 1)
  result = dict(instance = clf, train_indices = train_index, test_indices=test_index, y_true = y_test, y_pred = y_pred, acc = clf.score(X_test, y_test), mae = mean_absolute_error(y_test, y_pred), rmse = mean_squared_error(y_test, y_pred, squared = False), rmsle = mean_squared_log_error(y_test, y_pred, squared = False))
  if include_indices:
    result.update({"train_indices": train_index, "test_indices": test_index})
  return result

def MLP_vcra(X_sub, y_sub, y_bin_sub):
  mlp_vcra_features = ["own_speed", "own_course_rad", "target_speed", "target_course_rad", "dist_euclid", "azimuth_angle_target_to_own", "rel_movement_direction"]
  mlp_vcra_training_data = X_sub.loc[:, mlp_vcra_features].copy()

  sKF = StratifiedKFold(n_splits = 5, shuffle = True, random_state = 10)
  regr = make_pipeline(StandardScaler(), MLPRegressor(random_state = 10, max_iter = 300, hidden_layer_sizes = (256, 32), verbose = True, early_stopping = True, n_iter_no_change = 7))

  mlp_vcra_skf_results_df = pd.DataFrame(Parallel(n_jobs = -1)(delayed(evaluate_clf)(regr, mlp_vcra_training_data, y_sub, train_index, test_index) for (train_index, test_index) in tqdm.tqdm(sKF.split(X_sub, y_bin_sub), total = sKF.get_n_splits(X_sub, y_bin_sub))))
  # mlp_vcra_skf_results_df.to_pickle(f"source code/risk-prediction/code/result(s)/MLP_VCRA_result.pickle")

if __name__ == "__main__":
  parser = argparse.ArgumentParser(prog = "Train VCRA Model")
  parser.add_argument("--model", help = "Select Model:", default = "MLP", choices = ["MLP"])
  parser.add_argument("--use_subset", help = "Use a stratified subset (for \"RAM\" hungry models).", action = "store_true")
  args = parser.parse_args()

  dataframe = pd.read_pickle(f"source code/risk-prediction/code/result(s)/encountering_result.pickle")
  dataframe.loc[:, "ves_cri_bin"] = pd.cut(dataframe.ves_cri, bins = np.arange(0, 1.1, .2), right = True, include_lowest = True)
  X, y, y_bin = dataframe.iloc[:, :-2], dataframe.iloc[:, -2], dataframe.iloc[:, -1].astype("str")
  X_sub, _, y_sub, _, y_bin_sub, _ = train_test_split(X, y, y_bin, train_size = 0.35, random_state = 10, stratify = y_bin)
  fun_train = eval(f"{args.model}_vcra")
  args = (X_sub, y_sub, y_bin_sub) if args.use_subset else (X, y, y_bin)
  fun_train(*args)
  pass