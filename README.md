# ind320 Streamlit app

- Version: 3.0
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
├── modules/
│   ├── __init__.py
│   ├── analysis.py
│   ├── api.py
│   ├── session.py
│   └── db.py
│
├── pages/
│   ├── 2_page_four.py
│   ├── 3_new_A.py
│   ├── 4_page_two.py
│   ├── 5_page_three.py
│   ├── 6_new_B.py
│   └── 7_page_five.py
│
├── notebooks/
│
├── .gitginore
├── main.py
├── requirements.txt
└── README.md
```

### Modules/
Contains per v3.0, `analysis.py` with tailored plot functions, `session.py` for persisting variables in Streamlit and keep entry point arbitrary and `db.py` with a custom `MongoDB` handler.

### Notebooks/
All notebooks used to document development will be published here.

### Pages/
Contains per v3.0, 6 different pages as per task description. Naming convention used to reflect task description.

### Main.py
This file contains the main entry point for the application, and renders the front page.