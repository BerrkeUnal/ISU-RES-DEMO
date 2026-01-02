IsuRes - University Reservation System
IsuRes is a Streamlit-based reservation platform designed for university environments. It allows students, academicians, and admins to efficiently manage and book study rooms, laboratories, and classrooms.

🚀 Key Features
The system provides tailored experiences based on user roles:

Students: Can view available classrooms, make reservations for up to 3 hours, and perform check-ins within specific time windows.

Academicians: Have "Academic Priority," allowing them to override existing student reservations in case of scheduling conflicts.

Admins: Access a comprehensive dashboard with system statistics, user management (CRUD), classroom configuration, and full reservation logs.

🛠️ Technical Stack
Frontend: Streamlit with custom CSS for a modern UI.

Backend: Python 3.x.

Database: MySQL (Relational database management).

Communication: mysql-connector-python for database integration.

📋 Installation & Setup

1. Clone the Repository and Install Dependencies
   Ensure you have Python installed, then run:

Bash

pip install -r requirements.txt

2. Database Configuration
   Open your MySQL environment (e.g., MySQL Workbench).

Run the provided LibApp.sql script to create the Libapp database, tables, and demo values.

Update the database credentials in utils.py:

Python

def get_db_connection():
return mysql.connector.connect(
user="root",
password="YOUR_PASSWORD", # Change this
host="localhost",
database="Libapp"
)

3. Run the Application

   Bash:

streamlit run main.py

🛡️ System Rules & Logic
Check-in Window: Users must check in between 5 minutes before and 15 minutes after the reservation start time.

No-Show Penalty: Failure to check in results in an automatic "No-Show" status, which restricts the user from making new reservations for 24 hours.

Duration Limit: Single reservations are capped at a maximum of 3 hours.

Conflict Resolution: The system automatically checks for overlapping slots before confirming any booking.

📁 Project Structure
main.py: Entry point and sidebar navigation logic.

utils.py: Database connections, CSS styles, and core business logic.

views/auth.py: Login page design and authentication checks.

views/admin.py: Admin panel UI including statistics and management tabs.

views/user.py: User-facing pages for classroom browsing, booking, and notifications.

LibApp.sql: SQL script for database schema and initial data.
