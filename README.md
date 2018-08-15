# Viewport map

A map project that renders Google Map based on fusion table data. When a user clicks on any location from the map, the locations is saved in sqlite and Google Fusion Tables.

## Requirements

* Python 3.x
* Virtualenv

## Installation
(make sure you are in the project folder)

1. Create a virtualenv with python3:

    ```virtualenv venv -p python3```

2. Activate the virtualenv:

    ```. venv/bin/activate```

3. Install python requirements with pip

    ```pip install -r requirements.txt```

4. Run migrations

    ```python manage.py migrate```

5. Copy client_secrets.example.json to client_secrets.json and edit with google api credentials:

    ```cp client_secrets.example.json client_secrets.json```


To use this project you will need to activate Fusion Table API from https://console.cloud.google.com and generate OAuth 2.0 client IDs for that specific API.
After that you will need to create a Fusion Table from http://fusiontables.google.com/ and get it's table id.

You will also need to do the same for Google Maps API. Go to Google Console, activate the Maps JavaScript API and create API keys for it.

## Run the server
    GOOGLE_API_KEY=_API_KEY TABLE_ID=_TABLE_ID python manage.py runserver

## Running the tests
    python manage.py test


