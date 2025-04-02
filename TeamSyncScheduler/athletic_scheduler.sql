    -- Create the database

    CREATE DATABASE athletic_scheduler;

    USE athletic_scheduler;

 

    -- Create Users table

    CREATE TABLE users (

        user_id INT AUTO_INCREMENT PRIMARY KEY,

        username VARCHAR(50) NOT NULL UNIQUE,

        password VARCHAR(255) NOT NULL,

        role ENUM('coach', 'athlete') NOT NULL,

        team_id INT

    );

 

    -- Create Teams table

    CREATE TABLE teams (

        team_id INT AUTO_INCREMENT PRIMARY KEY,

        team_name VARCHAR(100) NOT NULL

    );

 

    -- Create Events table

    CREATE TABLE events (

        event_id INT AUTO_INCREMENT PRIMARY KEY,

        team_id INT,

        user_id INT,

        date DATE NOT NULL,

        time TIME NOT NULL,

        location VARCHAR(100),

        event_type ENUM('team', 'personal') NOT NULL,

        equipment TEXT,

        comments TEXT,

        rsvp ENUM('yes', 'no', 'pending') DEFAULT 'pending',

        FOREIGN KEY (team_id) REFERENCES teams(team_id),

        FOREIGN KEY (user_id) REFERENCES users(user_id)

    );

 

    -- Create Messages table

    CREATE TABLE messages (

        message_id INT AUTO_INCREMENT PRIMARY KEY,

        team_id INT,

        user_id INT,

        content TEXT NOT NULL,

        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (team_id) REFERENCES teams(team_id),

        FOREIGN KEY (user_id) REFERENCES users(user_id)

    );

 

    -- Create Feedback table

    CREATE TABLE feedback (

        feedback_id INT AUTO_INCREMENT PRIMARY KEY,

        user_id INT,

        event_id INT,

        fatigue_score INT CHECK (fatigue_score BETWEEN 1 AND 5),

        mental_score INT CHECK (mental_score BETWEEN 1 AND 5),

        notes TEXT,

        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (user_id) REFERENCES users(user_id),

        FOREIGN KEY (event_id) REFERENCES events(event_id)

    );

 

    -- Add foreign key to Users for team_id

    ALTER TABLE users ADD FOREIGN KEY (team_id) REFERENCES teams(team_id);

