# ind320 Streamlit app

- Version: 1.0
- Author: gsxbl

---

Deployed to Streamlit cloud [here.](https://ind320-gsxbl.streamlit.app)

---

## App structure
```
app/
├── .streamlit/
│   └── config.toml
│
├── data/
│   └── open-meteo-subset.csv
│
├── modules/
│   ├── __init__.py
│   └── fetch.py
│
├── pages/
│   ├── 2_page_two.py
│   ├── 3_page_three.py
│   └── 4_page_four.py
│
├── notebooks/
│
├── .gitginore
├── main.py
├── requirements.txt
└── README.md
```

### Modules/
Contains per v1.0, some custom functions for streamlit-cached reading of csv-files

### Notebooks/
All notebooks used to document development will be published here.

### Pages/
Contains per v1.0, four different pages as per task description

### Data
This folder contains the supplied data for use in compulsory assignment 1, which corresponds to v1.0.

### Main.py
This file contains the main entry point for the application, and renders the front page.