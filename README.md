# A Collision-Risk-Aware Skyline Routing Framework for Maritime Navigation

Research code for maritime route planning using AIS data, collision-risk estimates, and skyline queries. This repository is referenced by the 2024 and 2026 papers below.

## Publication

Patrik Thomas Michalski, Niko Preuß, Matthias Renz, Andreas Tritsarolis, Nikos Pelekis, Yannis Theodoridis (2026). **A Collision-Risk-Aware Skyline Routing Framework for Maritime Navigation.** In *27th IEEE International Conference on Mobile Data Management (MDM)*.

[DOI: 10.1109/MDM71479.2026.00017](https://doi.org/10.1109/MDM71479.2026.00017) · [Machine-readable citation](CITATION.cff)

**Earlier paper:** Patrik Thomas Michalski, Niko Preuß, Matthias Renz, Andreas Tritsarolis, Yannis Theodoridis, and Nikos Pelekis (2024). **Collision-Risk-Aware Ship Routing.** In *32nd ACM International Conference on Advances in Geographic Information Systems (SIGSPATIAL)*, pp. 545–548. [DOI: 10.1145/3678717.3691316](https://doi.org/10.1145/3678717.3691316).

Both papers link to this repository. That does not establish that the current commit alone reproduces every reported experiment.

## Repository contents

| Path | Purpose |
| --- | --- |
| code/src/frame/runner.py | Routing experiment entry point. |
| code/src/frame/RP_main.py | Additional experimental and visualization routines. |
| code/src/frame/VCRA_init.py | AIS preprocessing and model-data preparation. |
| code/src/frame/algorithms/ARSC_FC/ | Advanced Route Skyline Computation and supporting routines. |
| code/.config/ARSC/ARSC.config | Routing parameters and input-data locations. |
| code/.settings/requirements.txt | Original environment snapshot, retained for provenance. |
| code/data/.ML_model/ | Supplied serialized model and generated model data. |
| code/data/.embedding/ | Supplied serialized embedding. |
| code/data/.result/ | Experiment outputs. |
| Dockerfile | Container recipe for the experiment runner. |

## Data and configuration

Raw AIS CSV files and harbour geometry are not included. The papers reference the [AIS dataset description](https://doi.org/10.1016/j.dib.2021.107782) and [Zenodo record 6323416](https://zenodo.org/records/6323416). Check the data source's license separately.

Edit code/.config/ARSC/ARSC.config to supply the H3 resolution, source and destination coordinates, start date, and input paths. The “undefined” entries are placeholders, not usable experiment settings. Preprocessing expects CSV fields including t, vessel_id, lon, lat, speed, and course; t is read as a Unix timestamp in milliseconds.

Place AIS CSV files in code/data/input/ais/ and the harbour geometry dataset at code/data/input/harbours/, or adjust the corresponding paths. The runner creates code/data/.ML_model/geoDataframe.pickle from the input data when it is absent. Experiment outputs go under code/data/.result/.

Serialized model and embedding files are retained as experiment inputs. Only load serialized files from sources you trust.

## Environment and execution

The Docker recipe uses Python 3.10.14. The dependency file is a broad historical environment export, including Anaconda and platform-specific packages, rather than a portable minimal requirements file. Installing that export unchanged may fail on another platform. The code uses the H3 3.x API, including polyfill and k_ring_distances.

After preparing a compatible geospatial/scientific Python environment and completing the data and configuration steps, the entry point is:

```sh
python code/src/frame/runner.py
```

Paths are resolved relative to the checkout. A fresh full routing experiment has not been validated during this cleanup. The container recipe also depends on resolving the historical environment; it is not a verified ready-to-run image.

## License

The repository's original code and accompanying documentation are licensed under the [MIT License](LICENSE). External AIS data, dependencies, and linked publications retain their own licensing terms.

## Citation and questions

Please cite the relevant paper when using these materials, and record the repository commit, data version, and environment for reproducibility. Questions and reproducibility problems can be raised in [Issues](https://github.com/stu207680/risk-prediction/issues).
