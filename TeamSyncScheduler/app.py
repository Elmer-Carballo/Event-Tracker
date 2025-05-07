from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import hashlib
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secure session key

# Database Connection Function
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            database='event_scheduler_DB',
            user='root',
            password='J.Cole28'  # Replace with your actual MySQL root password
        )
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Database Initialization
def init_db():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database for initialization")
        return
    c = conn.cursor()
    
    # Create tables if they don’t exist
    c.execute('''CREATE TABLE IF NOT EXISTS teams (
        team_id INT AUTO_INCREMENT PRIMARY KEY,
        team_name VARCHAR(100) NOT NULL
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        hashed_password VARCHAR(255) NOT NULL,
        role ENUM('coach', 'player') NOT NULL,
        team_id INT,
        notification_preference TINYINT DEFAULT 1,
        FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE SET NULL
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS events (
        event_id INT AUTO_INCREMENT PRIMARY KEY,
        date DATE NOT NULL,
        time TIME NOT NULL,
        location VARCHAR(100),
        type ENUM('team', 'personal') NOT NULL,
        notes TEXT,
        required_items TEXT,
        creator_id INT NOT NULL,
        team_id INT,
        FOREIGN KEY (creator_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE SET NULL
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
        attendance_id INT AUTO_INCREMENT PRIMARY KEY,
        event_id INT NOT NULL,
        user_id INT NOT NULL,
        status ENUM('Yes', 'No', 'Maybe') NOT NULL,
        UNIQUE KEY unique_attendance (event_id, user_id),
        FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS fitness_feedback (
        feedback_id INT AUTO_INCREMENT PRIMARY KEY,
        event_id INT NOT NULL,
        user_id INT NOT NULL,
        fatigue_level INT CHECK (fatigue_level BETWEEN 1 AND 5),
        mental_state INT CHECK (mental_state BETWEEN 1 AND 5),
        notes TEXT,
        UNIQUE KEY unique_feedback (event_id, user_id),
        FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        message_id INT AUTO_INCREMENT PRIMARY KEY,
        sender_id INT NOT NULL,
        team_id INT NOT NULL,
        content TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        event_id INT,
        FOREIGN KEY (sender_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE CASCADE,
        FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE SET NULL
    )''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully")

# Hash Password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Routes

# Login
@app.route('/', methods=['GET', 'POST'])
def login():
    # Clear any previous session data when accessing login page
    if request.method == 'GET':
        session.clear()
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Input validation
        validation_errors = []
        
        # Check if username is provided
        if not username:
            validation_errors.append("Username is required")
        
        # Check if password is provided
        if not password:
            validation_errors.append("Password is required")
            
        # If there are validation errors, flash them and return to login
        if validation_errors:
            for error in validation_errors:
                flash(error)
            return render_template('login.html')
            
        # Hash the password for database comparison
        hashed_password = hash_password(password)
        
        # Try to establish database connection
        conn = get_db_connection()
        if not conn:
            flash('Database connection failed. Please try again later.')
            return render_template('login.html')
            
        try:
            c = conn.cursor(dictionary=True)
            
            # First check if the username exists
            c.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = c.fetchone()
            
            if not user:
                # Username not found, but don't be too specific in error message (security best practice)
                flash('Invalid username or password')
                return render_template('login.html')
                
            # Now check if the password matches
            if user['hashed_password'] != hashed_password:
                flash('Invalid username or password')
                return render_template('login.html')
                
            # Login successful - store user data in session
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['team_id'] = user['team_id']
            session['notification_preference'] = user['notification_preference']
            
            # Log successful login (optional)
            print(f"User {username} logged in successfully")
            
            # Redirect to dashboard
            return redirect(url_for('dashboard'))
            
        except Error as e:
            # Log the actual error for debugging
            print(f"Database error during login: {e}")
            flash('An error occurred during login. Please try again.')
        finally:
            conn.close()
            
    # GET request or failed POST, show login page
    return render_template('login.html')

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data with proper validation
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', '')
        team_id_str = request.form.get('team_id', '')
        
        # Comprehensive validation with specific error messages
        validation_errors = []
        
        # Username validation - Check length and allowed characters
        if not username:
            validation_errors.append("Username is required")
        elif len(username) < 3:
            validation_errors.append("Username must be at least 3 characters long")
        elif len(username) > 50:
            validation_errors.append("Username is too long (maximum 50 characters)")
        elif not username.isalnum():
            validation_errors.append("Username must contain only letters and numbers")
            
        # Password validation - Ensure minimum security
        if not password:
            validation_errors.append("Password is required")
        elif len(password) < 6:
            validation_errors.append("Password must be at least 6 characters long")
            
        # Role validation - Must be either 'coach' or 'player'
        if not role:
            validation_errors.append("Role is required")
        elif role not in ['coach', 'player']:
            validation_errors.append("Invalid role selection")
            
        # Team ID validation - Must be a positive integer
        try:
            team_id = int(team_id_str)
            if team_id <= 0:
                validation_errors.append("Team ID must be a positive number")
        except ValueError:
            validation_errors.append("Team ID must be a number")
            
        # If there are validation errors, flash them and return to registration form
        if validation_errors:
            for error in validation_errors:
                flash(error)
            return render_template('register.html')
            
        # Hash the password for storage
        hashed_password = hash_password(password)
        
        # Try to establish database connection
        conn = get_db_connection()
        if not conn:
            flash('Database connection failed. Please try again later.')
            return render_template('register.html')
            
        try:
            c = conn.cursor()
            
            # Check if username already exists
            c.execute("SELECT user_id FROM users WHERE username = %s", (username,))
            if c.fetchone():
                flash('Username already taken. Please choose another username.')
                return render_template('register.html')
                
            # Check if team exists
            c.execute("SELECT team_id FROM teams WHERE team_id = %s", (team_id,))
            if not c.fetchone():
                flash('Team ID does not exist. Please enter a valid team ID.')
                return render_template('register.html')
                
            # All validations passed, insert new user
            c.execute("""
                INSERT INTO users (username, hashed_password, role, team_id) 
                VALUES (%s, %s, %s, %s)
            """, (username, hashed_password, role, team_id))
            
            conn.commit()
            
            # Registration successful - flash success message
            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))
            
        except mysql.connector.IntegrityError as e:
            # Handle database integrity errors
            print(f"Database integrity error: {e}")
            if "Duplicate entry" in str(e):
                flash('Username already exists. Please choose another username.')
            else:
                flash('An error occurred during registration. Please try again.')
        except Error as e:
            # Handle other database errors
            print(f"Database error during registration: {e}")
            flash('An error occurred during registration. Please try again.')
        finally:
            conn.close()
            
    # GET request or failed POST, show registration form
    return render_template('register.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed')
        return redirect(url_for('login'))
    c = conn.cursor()
    
    # Calendar Events
    if session['role'] == 'coach':
        c.execute("SELECT * FROM events WHERE team_id = %s OR creator_id = %s", 
                 (session['team_id'], session['user_id']))
    else:
        c.execute("SELECT * FROM events WHERE team_id = %s OR creator_id = %s", 
                 (session['team_id'], session['user_id']))
    events = c.fetchall()
    
    # To-Do List (events for today)
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute("SELECT * FROM events WHERE (team_id = %s OR creator_id = %s) AND date = %s", 
             (session['team_id'], session['user_id'], today))
    todos = c.fetchall()
    
    conn.close()
    return render_template('dashboard.html', events=events, todos=todos, role=session['role'])

# Add Event
@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        date = request.form['date']
        time = request.form['time']
        location = request.form['location']
        event_type = request.form['type'] if session['role'] == 'coach' else 'personal'
        notes = request.form['notes']
        required_items = request.form.get('required_items', '') if session['role'] == 'coach' else ''
        
        conn = get_db_connection()
        if not conn:
            flash('Database connection failed')
            return redirect(url_for('dashboard'))
        c = conn.cursor()
        team_id = session['team_id'] if event_type == 'team' and session['role'] == 'coach' else None
        c.execute("INSERT INTO events (date, time, location, type, notes, required_items, creator_id, team_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", 
                 (date, time, location, event_type, notes, required_items, session['user_id'], team_id))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    
    return render_template('event_form.html', action='Add', role=session['role'])

# Edit Event
@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed')
        return redirect(url_for('dashboard'))
    c = conn.cursor()
    c.execute("SELECT * FROM events WHERE event_id = %s", (event_id,))
    event = c.fetchone()
    
    if not event or (event[7] != session['user_id'] and session['role'] != 'coach'):
        conn.close()
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        date = request.form['date']
        time = request.form['time']
        location = request.form['location']
        notes = request.form['notes']
        required_items = request.form.get('required_items', '') if session['role'] == 'coach' else event[6]
        c.execute("UPDATE events SET date = %s, time = %s, location = %s, notes = %s, required_items = %s WHERE event_id = %s", 
                 (date, time, location, notes, required_items, event_id))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    
    conn.close()
    return render_template('event_form.html', action='Edit', event=event, role=session['role'])

# Submit Attendance
@app.route('/submit_attendance/<int:event_id>', methods=['POST'])
def submit_attendance(event_id):
    if 'user_id' not in session or session['role'] != 'player':
        return redirect(url_for('dashboard'))
    
    status = request.form['status']
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed')
        return redirect(url_for('dashboard'))
    c = conn.cursor()
    # Use INSERT ... ON DUPLICATE KEY UPDATE to mimic SQLite's INSERT OR REPLACE
    c.execute("""
        INSERT INTO attendance (event_id, user_id, status) 
        VALUES (%s, %s, %s) 
        ON DUPLICATE KEY UPDATE status = %s
    """, (event_id, session['user_id'], status, status))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

# Submit Fitness Feedback
@app.route('/submit_feedback/<int:event_id>', methods=['GET', 'POST'])
def submit_feedback(event_id):
    if 'user_id' not in session or session['role'] != 'player':
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        fatigue = int(request.form['fatigue'])
        mental = int(request.form['mental'])
        notes = request.form['notes']
        conn = get_db_connection()
        if not conn:
            flash('Database connection failed')
            return redirect(url_for('dashboard'))
        c = conn.cursor()
        # Use INSERT ... ON DUPLICATE KEY UPDATE to mimic SQLite's INSERT OR REPLACE
        c.execute("""
            INSERT INTO fitness_feedback (event_id, user_id, fatigue_level, mental_state, notes) 
            VALUES (%s, %s, %s, %s, %s) 
            ON DUPLICATE KEY UPDATE fatigue_level = %s, mental_state = %s, notes = %s
        """, (event_id, session['user_id'], fatigue, mental, notes, fatigue, mental, notes))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    
    return render_template('feedback.html', event_id=event_id)

# Send Team Message (Coach Only)
@app.route('/send_message', methods=['POST'])
def send_message():
    if 'user_id' not in session or session['role'] != 'coach':
        return redirect(url_for('dashboard'))
    
    content = request.form['content']
    event_id = request.form.get('event_id', None) or None  # Convert empty string to NULL
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed')
        return redirect(url_for('dashboard'))
    c = conn.cursor()
    c.execute("INSERT INTO messages (sender_id, team_id, content, event_id) VALUES (%s, %s, %s, %s)", 
             (session['user_id'], session['team_id'], content, event_id))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

# View Messages
@app.route('/messages')
def view_messages():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    if not conn:
        flash('Database connection failed')
        return redirect(url_for('dashboard'))

    c = conn.cursor()

    # Retrieve messages for the player's team
    c.execute("""
        SELECT m.content, m.timestamp, u.username 
        FROM messages m 
        JOIN users u ON m.sender_id = u.user_id
        WHERE m.team_id = %s
        ORDER BY m.timestamp DESC
    """, (session['team_id'],))
    
    messages = c.fetchall()
    conn.close()
    return render_template('messages.html', messages=messages, role=session['role'])


# Toggle Notifications
@app.route('/toggle_notifications', methods=['POST'])
def toggle_notifications():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    pref = 1 if request.form.get('notifications') == 'on' else 0
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed')
        return redirect(url_for('dashboard'))
    c = conn.cursor()
    c.execute("UPDATE users SET notification_preference = %s WHERE user_id = %s", 
             (pref, session['user_id']))
    conn.commit()
    conn.close()
    session['notification_preference'] = pref  # Update session
    return redirect(url_for('dashboard'))

# View Feedback (Coach Feature)
@app.route('/view_feedback')
def view_feedback():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    # Only allow coaches to access this page
    if session['role'] != 'coach':
        flash('Access denied: Coach permission required')
        return redirect(url_for('dashboard'))
        
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed')
        return redirect(url_for('dashboard'))
        
    c = conn.cursor(dictionary=True)
    
    # Get all feedback for events associated with this coach's team
    c.execute("""
        SELECT ff.feedback_id, ff.event_id, e.date, e.time, e.location, 
               u.username AS player_name, ff.fatigue_level, ff.mental_state, ff.notes
        FROM fitness_feedback ff
        JOIN users u ON ff.user_id = u.user_id
        JOIN events e ON ff.event_id = e.event_id
        WHERE e.team_id = %s
        ORDER BY e.date DESC, e.time DESC
    """, (session['team_id'],))
    
    feedback_entries = c.fetchall()
    conn.close()
    
    return render_template('view_feedback.html', feedback_entries=feedback_entries)


# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
