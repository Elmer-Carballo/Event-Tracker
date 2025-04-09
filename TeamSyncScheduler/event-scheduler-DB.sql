-- Create the database
CREATE DATABASE event_scheduler;
USE event_scheduler;

-- Table: users
-- Stores coach and athlete info (username, password, role, team, notifications)
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    role ENUM('coach', 'player') NOT NULL, -- Matches your app's 'coach' and 'player' roles
    team_id INT, -- Can be NULL if not yet assigned to a team
    notification_preference TINYINT DEFAULT 1, -- 1 = on, 0 = off
    FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE SET NULL
);

-- Table: teams
-- Stores team information (not explicitly in your SQLite, but implied by team_id)
CREATE TABLE teams (
    team_id INT AUTO_INCREMENT PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL
);

-- Table: events
-- Stores team and personal events
CREATE TABLE events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL, -- Changed from TEXT to DATE for better querying
    time TIME NOT NULL, -- Changed from TEXT to TIME for consistency
    location VARCHAR(100),
    type ENUM('team', 'personal') NOT NULL,
    notes TEXT,
    required_items TEXT, -- Coach-only field in your app
    creator_id INT NOT NULL,
    team_id INT, -- NULL for personal events
    FOREIGN KEY (creator_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE SET NULL
);

-- Table: attendance
-- Stores athlete RSVPs for events
CREATE TABLE attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    user_id INT NOT NULL,
    status ENUM('Yes', 'No', 'Maybe') NOT NULL,
    UNIQUE KEY unique_attendance (event_id, user_id), -- Ensures one RSVP per user per event
    FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Table: fitness_feedback
-- Stores athlete feedback on events
CREATE TABLE fitness_feedback (
    feedback_id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    user_id INT NOT NULL,
    fatigue_level INT CHECK (fatigue_level BETWEEN 1 AND 5),
    mental_state INT CHECK (mental_state BETWEEN 1 AND 5),
    notes TEXT,
    UNIQUE KEY unique_feedback (event_id, user_id), -- One feedback per user per event
    FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Table: messages
-- Stores coach messages to the team
CREATE TABLE messages (
    message_id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT NOT NULL,
    team_id INT NOT NULL,
    content TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    event_id INT,
    FOREIGN KEY (sender_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE SET NULL
);

-- Fix the users table foreign key (added after teams is created)
ALTER TABLE users ADD FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE SET NULL;
