# Trekking Management Application

A role-based web application for managing trekking activities, users, trek staff, bookings, and participants.

Developed as part of the Modern Application Development I course project.

## Overview

The Trekking Management Application provides a centralized platform for managing trekking operations. Different users get access to features based on their roles, including trekking management, staff management, user management, bookings, and participant tracking.

## User Roles

### Trekker / User

- Register and log in
- Browse and search available treks
- Book treks
- Cancel bookings
- View booking details and booking history
- Manage profile information

### Trek Staff

- Log in through staff authentication
- View assigned treks
- Manage assigned trek information
- View and manage trek participants
- Update trek-related information

### Admin

- Manage users
- Manage trek staff
- Create, edit, and delete treks
- Manage bookings
- Assign staff to treks
- Monitor trek and booking status

## Key Features

- Role-based authentication and authorization
- User registration and login
- Admin, staff, and user dashboards
- Trek creation and management
- Trek staff assignment
- Trek booking and cancellation
- Prevention of duplicate bookings
- Prevention of overbooking
- Booking and trek status tracking
- Participant management
- User booking history
- Profile management
- Search and filtering functionality
- Form validation and access control

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Application development |
| Flask | Web application framework |
| SQLite | Database |
| Jinja2 | Server-side templating |
| HTML | Frontend structure |
| CSS | Frontend styling |

## Project Structure

```text
trekking-management-application/
│
├── app.py                 # Flask application and backend logic
├── trek.db                # SQLite database with demo data
├── README.md
├── .gitignore
│
├── templates/             # HTML/Jinja2 templates
│   ├── admin_*.html
│   ├── staff_*.html
│   └── user_*.html
│
└── static/
    ├── css/               # Application stylesheets
    └── images/            # Application images and assets
```

## Running the Application

### 1. Clone the repository

```bash
git clone https://github.com/yashvardhan2066-eng/trekking-management-application.git
cd trekking-management-application
```

### 2. Create a virtual environment

Creating a virtual environment is recommended.

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install Flask

```bash
pip install flask
```

### 4. Run the application

```bash
python app.py
```

### 5. Open the application

Open the local URL displayed in the terminal in a web browser.

## Project Status

This is an academic/demo project developed to demonstrate web application development using Flask, SQLite, Jinja2, HTML, and CSS.

## Future Improvements

- Deploy the application to a cloud platform
- Improve UI responsiveness and accessibility
- Add email notifications for bookings
- Add automated testing
- Introduce a production database such as PostgreSQL
- Add REST API support

## Author

**Yashvardhan Reddy D**

GitHub: https://github.com/yashvardhan2066-eng
