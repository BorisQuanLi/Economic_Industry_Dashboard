
### Description

This Project makes API calls to ingest the most recent 8 quarters of financial statements filed by the S&P 500 publicly listed companies, then stores the data on a Postgres DB, utilizing the Adapter and Model-View-Controller (MVC) design patterns along the way.

A Flask API app allows the user to query aggregate and company-level data such as average quarterly revenue, cost, and price/earnings ratios, returning the results in JSON format in a web browser.

Various plots based on these data can be viewed in an interactive dashboard in a browser, where a user can select different economic sectors and sub-sectors, companies, and financial performance indicators — for example, a cross-sector comparison of average quarterly earnings over the last 8 quarters.

### Prerequisite Technologies

Backend:

- PostgreSQL 11.13
- Flask 1.1.2
- Python 3.8
- Pandas 1.1.4
- Docker 19.03.12
- Kubernetes v1.20.2

Frontend

- Streamlit 0.73.1 (a Python library)

### Getting Started

Once all the technologies are installed, clone this project's repo in your local machine.

* Backend

To spin up the Flask app and access the back-end Postgres DB, navigate to the backend folder from the project directory's root level:

$ cd backend/

Then execute:

backend $ python3 run.py 

Paste this url in a browser:

http://127.0.0.1:5000/

* Frontend

To experience the frontend dashboard, navigate to the frontend folder from the project directory's root level:

$ cd frontend/

frontend $ streamlit run src/index.py 


### Please check out a [recorded demo](https://www.youtube.com/watch?v=-OesaExIybA) of the dashboard.

