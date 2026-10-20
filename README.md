
# Online Voting System

A web-based voting application developed using Python and Django.

## Features

- User registration and login
- Election and candidate management
- One vote per user per election
- Election opening and closing checks
- Election results with vote percentages
- Bar chart for vote distribution
- Django Admin panel
- Automated tests

## Technologies Used

- Python
- Django
- SQLite
- HTML
- Bootstrap
- Matplotlib

## Setup

1. Install Python 3.12.
2. Create and activate a virtual environment.
3. Install the required packages:

   `python -m pip install -r requirements.txt`

4. Apply migrations:

   `python manage.py migrate`

5. Create an administrator:

   `python manage.py createsuperuser`

6. Start the development server:

   `python manage.py runserver`

7. Open `http://127.0.0.1:8000/`.

## Run Tests

`python manage.py test`

## Note

This project is intended for educational use and is not a production-ready election platform.
