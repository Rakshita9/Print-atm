\# Print ATM - QR Based PDF Printing Prototype



A Django-based prototype for a self-service printing system that allows users to upload PDF files and send them to a locally connected printer.



\## Features



\- PDF file upload

\- PDF validation

\- Local printer integration

\- Automatic PDF printing on Windows

\- REST API endpoint for print requests

\- SQLite database for local development

\- Temporary uploaded files excluded from Git



\## Tech Stack



\- Python

\- Django

\- Django REST Framework

\- PyMuPDF

\- pywin32

\- SQLite



\## How It Works



1\. User uploads a PDF through the API.

2\. Django validates the uploaded file.

3\. The PDF is processed using PyMuPDF.

4\. The application sends the document to the configured Windows printer.

5\. The document is printed locally.



\## Setup
### 1. Clone the repository

```bash
git clone <repository-url>
cd Print-atm

step 2:-
Create a virtual environment
python -m venv venv

step 3:-
Activate the virtual environment

Windows PowerShell:
venv\Scripts\Activate.ps1

step 4:-

Install dependencies

pip install -r requirements.txt


step 5:-
Run migrations
python manage.py migrate

step 6:-
Start the development server
python manage.py runserver

