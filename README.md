### Ref. https://github.com/codeforpdx/dwellingly-app

# Description

This Project extracts the last 8 quarters of financial statements filed by the S&P 500 publicly listed companies and stores the data on a Postgres DB, utilizing the Adapter and Model-View-Controller (MVC) design patterns along the way.

A Flask API app allows the user to query both aggregate and company-level data such as average quarterly revenue, cost, and price/earnings ratios, returning the results in JSON format in a web browser.

Various plots based these data can be viewed in an interactive dashboard in a broswer, where a user can select sector, sub-sector, company, and the financial-performance indicator.  An example is cross-sector comparision of average quarterly earnings over the last 8 quarters.

# Prerequisite Technologies

* Backend:

Postgress
Flask
Python 3.8
Pandas (?)
Docker (Version?)
Kubernetes

* Frontend

Streamlit (a Python library)

# Getting Started

Once all the technologies are installed, clone this project's repo in the local drive of your local machine.

* To spin up the Flask app and access the back-end Postgres DB, navigate to the backend folder from the project directory's root level:

$ cd backend/

Then execute:

backend $ python3 run.py 

Paste this url in a browser:

http://127.0.0.1:5000/

* To experience the frontend dashboard, navigate to the frontend folder from the project directory's root level:

$ cd frontend/

frontend $ streamlit run src/index.py 

[Dashboard](https://docs.google.com/document/d/e/2PACX-1vR32tVoSvUYB9-jgy_jT3-YbqrjJxQw8pXt13lmcwcjT7hfUW-2L4C5LJG5-BooBSDPGmUDvryonoaL/pub)

?? Talk about containerization and deploying the project on the appropriate AWS instances?
