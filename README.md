## 1. Introduction
The Event Tracker is a website designed to make organizing ones schedule easier, more specifically for athletes and coaches.

### 1.1 Purpose 
>This document details the functions and certain design elements of the Event Tracker website.

### 1.2 Intended Audience and Reading Suggestions
>This document is primarily intended to explain the requirements, value, and functionality of the event tracker.

### 1.3 Product Scope
>The event tracker is intended to streamline schedule organization for athletes. As some extra features, it allows for coaches and athletes to communicate and connect with one another.


## 2. Overall Description

### 2.1 Product Perspective
>The event tracker is built to assist athletes and coaches at Fresno Pacific University, and relies on a database to store login information
>
### 2.2 Product Functions
>Major functions include: event scheduling, account registering, announcement feature, player feedback forms.

### 2.3 User Classes and Characteristics
>The two user classes that are expected to make use of this are coaches and athletes who need a way to better organize time. It's to be assumed that they will have basic technical expertise and can make use of the website whenever needed.

### 2.4 User Documentation
>Users will have documentation instructions on how to get the application up and running. There will also be pop-up messages where needed to help guide users within the app (eg., Registration and Login corrections).

### 2.5 Assumptions and Dependencies
>It is assumed that
>* The athletes and coaches are to use this fairly often
>* The database functions without any hiccups
>* Coaches will tell their athletes with team code is unique to their teams


## 3. External Interface Requirements

### 3.1 User Interfaces

> * **Login**
[Login](ScreenImages/Login.png)

> * **Register**
[Register](ScreenImages/Register.png)

> * **Coach Dashboard**
[Coach Dashboard](ScreenImages/CoachDashboard.png)

> * **Coach Add Event**
[Coach Add Event](ScreenImages/CoachAddEvent.png)

>* **Coach Edit Event**
[Coach Edit Event](ScreenImages/CoachEditEvent.png)

> * **Coach View Player Feedback**
[Coach View Player Feedback](ScreenImages/CoachViewPlayerFeedback.png)

> * **View Messages**
[View Messages](ScreenImages/ViewMessages.png)

> * **Player Dashboard**
[Player Dashboard](ScreenImages/PlayerDashboard.png)

> * **Player Add Event**
[Player Add Event](ScreenImages/PlayerAddEvent.png)

> * **Player Edit Event**
[Player Edit Event](ScreenImages/PlayerEditEvent.png)

> * **Player Feedback Form**
[Player Feedback Form](ScreenImages/PlayerFeedbackForm.png)


### 3.2 Hardware Interfaces
>The hardware relies on both the site to be open and the database to be fully functional

### 3.3 Software Interfaces
>Our software works by communicating with a Flask API that is in charge of handling multiple operations, and has an internal calendar to keep track of events that were added by both coaches and players

### 3.4 Communications Interfaces
>In order to access the Operation Registration website, it is necessary to have an internet connection, web browser, and access to the Event Tracker's domain.


## 4. System Features

### 4.1 Login Screen
#### 4.1.1 Description
>This is where the user signs in with their username and password. If they do not have an account, they can register with a name, password, team ID and either as a player or a coach.


### 4.2 Dashboard
#### 4.2.1 Description
>This is the main page that the user sees, how it appears depends on if the user is a player or a coach.

### 4.3 Feedback submission screen (player)
#### 4.3.1 Description
>This page allows for the user to submit some feedback on how they are feeling, with a scale on 1-5 on how they are both physically and mentally, as well as a note to describe in more detail how they feel.

### 4.4 Add event
#### 4.4.1 Description
>This is where the user can add an event to their calendar. Both players and coaches have access to it, and if today is the same day that the event starts, it will be displayed on the dashboard.

## 5. Other Nonfunctional Requirements

### 5.1 Software Quality Attributes
### 5.1.1 Ease of Use
>It is imperative that the website be intuitive and simple to use, as the primary objective is to minimize time spent creating the schedules.


# Event-Tracker
The event tracker created for CSSE-350: Software Engineering.


**Steps to use "app.py"**

1) Install MySQL Connector:
    - Open a terminal (MacOS: Terminal; Windows: Command Prompt or PowerShell).
    - Run: pip install mysql-connector-python
    - Verify it’s installed: python -c "import mysql.connector; print('MySQL Connector is ready!')"
    - If you get an error, try pip3 install mysql-connector-python or ensure you’re using the correct Python environment.
  
2) Set Up MySQL:
    - Ensure MySQL is installed and running.
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
