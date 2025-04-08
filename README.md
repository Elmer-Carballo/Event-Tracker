# Event-Tracker
The event tracker created for CSSE-350: Software Engineering.


**Steps to use "app.py"**

1) Install MySQL Connector:
    - Open a terminal (MacOS: Terminal; Windows: Command Prompt or PowerShell).
    - Run: pip install mysql-connector-python
    - Verify it’s installed: python -c "import mysql.connector; print('MySQL Connector is ready!')"
    - If you get an error, try pip3 install mysql-connector-python or ensure you’re using the correct Python environment.
  
2) Set Up MySQL:
    - Ensure MySQL is installed and running on both students’ computers (MacOS and Windows). If not, follow the installation steps from the workbook (Task 0.1).
    - Log into MySQL: mysql -u root -p and enter your root password.
  
3) Create the Database:
    - Copy the SQL from the event-scheduler-DB.db file
  
4) Update the Password in app.py:
    - Open the updated app.py in your code editor.
    - Find this line in get_db_connection():
          password='YOUR_ROOT_PASSWORD
    - Replace 'YOUR_ROOT_PASSWORD' with the actual password you set for the MySQL root user during installation. For example:
          password = 'mysecretpassword'

5) Run the App:
   - Start MySQL if it’s not running:
          MacOS: mysql.server start
          Windows: Ensure the MySQL service is running (check Task Manager or Services).
  - Run the app: python app.py (or python3 app.py on MacOS).
  - Open a browser and go to http://127.0.0.1:5000/ to test the login page.


**What to Expect**
- First Run: The init_db() function will create the tables if they don’t exist. If you already ran the SQL manually, it won’t overwrite your data (due to IF NOT EXISTS).
- Behavior: The app should function exactly as before, but now it uses MySQL instead of SQLite. All routes (login, register, dashboard, etc.) and HTML templates will work without changes.
- Errors: If you see errors, check the terminal output:
    “Access denied”: Wrong password in get_db_connection().
    “Database not found”: Ensure athletic_scheduler exists (run the SQL).
    “Module not found”: Install mysql-connector-python.
