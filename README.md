# ind320 Streamlit app

- Version: 4.0
- Author: gsxbl

---

Deployed to Streamlit cloud [here.](https://ind320-gsxbl.streamlit.app)

---

## App file structure
```
app/
├── .streamlit/
│   └── config.toml
│
├── modules/
│   ├── __init__.py
│   ├── analysis.py
│   ├── api.py
│   ├── db.py
│   ├── geo.py
│   ├── header.py
│   ├── sarimax.py
│   ├── session.py
│   └── Snow_drift.py
│
├── pages/
│   ├── 1_map.py
│   ├── 2_chart2.py
│   ├── 3_frequency_analysis.py
│   ├── 4__line_chart.py
│   ├── 5_historical.py
│   ├── 6_anomalies.py
│   ├── 7_page_five.py
│   ├── 8_snow.py
│   ├── 9_correlation.py
│   ├── 10_forecasting.py
│   └── 11_settings.py
│
├── notebooks/
│   ├── project_work_part1.ipynb
│   ├── project_work_part2.ipybn
│   ├── project_work_part3.ipybn
│   └── project_work_part4.ipynb
│
├── .gitginore
├── main.py
├── requirements.txt
└── README.md
```
### Data/
This folder contains the `file.geojson` which has been downloaded from [Norges Vassdrag- og Energidirektorat](https://temakart.nve.no/tema/nettanlegg).
### Modules/
As of version 4.0 contains;
- `analysis.py` with tailored plotting functions.
- `api.py` defines an api wrapper for the `OpenMeteo` api.
- `db.py` defines a custom `MongoDB` handler. The `Mongo` database has been pre-populated with data from the [Elhub](https://api.elhub.no) api.
- `geo.py` defines a handler object for geo posistions.
- `header.py` defines a header object for rendering on all pages
- `sarimax.py` defines a handler object for `statsmodels` SARIMAX analysis.
- `session.py` for persisting variables in Streamlit and to keep app entry point arbitrary.
- `Snow_drift.py` a custom compluational script provided as course material.

### Notebooks/
All notebooks used to document development are published here.

### Pages/
Contains per v4.0, 11 different pages as per task descriptions located in the `.ipynb` files in `notebooks/`.
The naming convention is used to reflect the contents of each task. This is overridden by running `main.py`, which groups and renders the page names slightly different.

### Main.py
This file contains the main entry point for the application, and renders the front page.