parser_sc BY ALEXANDR KHAKHANOVSKYI There is a test parser for scrapping club website.

HOW TO INSTALL (FOR WINDOWS) git clone https://github.com/hahan18/parser_sc.git

Make venv using: python -m venv venv, Then use: venv\Scripts\activate.

Run pip install -r requirements.txt

Make .env file in root directory with fields as follow:
USER=            # ('postgres' set by default)
PASSWORD=        # ('password' for your DB user)
HOST=            # ('localhost' set by default)
PORT=            # ('5432' set by default)
