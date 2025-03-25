from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime
import hashlib
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secure session key

# Database Initialization
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (user_id INTEGER PRIMARY KEY, username TEXT UNIQUE, hashed_password TEXT, 
                  role TEXT, team_id INTEGER, notification_preference INTEGER DEFAULT 1)''')
    c.execute('''CREATE TABLE IF NOT EXISTS events 
                 (event_id INTEGER PRIMARY KEY, date TEXT, time TEXT, location TEXT, 
                  type TEXT, notes TEXT, required_items TEXT, creator_id INTEGER, team_id INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS attendance 
                 (attendance_id INTEGER PRIMARY KEY, event_id INTEGER, user_id INTEGER, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS fitness_feedback 
                 (feedback_id INTEGER PRIMARY KEY, event_id INTEGER, user_id INTEGER, 
                  fatigue_level INTEGER, mental_state INTEGER, notes TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages 
                 (message_id INTEGER PRIMARY KEY, sender_id INTEGER, team_id INTEGER, 
                  content TEXT, timestamp TEXT, event_id INTEGER)''')
    conn.commit()
    conn.close()

# Hash Password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Routes

# Login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND hashed_password = ?", 
                 (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            session['role'] = user[3]
            session['team_id'] = user[4]
            return redirect(url_for('dashboard'))
        flash('Invalid credentials')
    return render_template('login.html')

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])
        role = request.form['role']
        team_id = int(request.form['team_id'])  # Simplified; real app would validate team
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, hashed_password, role, team_id) VALUES (?, ?, ?, ?)", 
                     (username, password, role, team_id))
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already taken')
        conn.close()
    return render_template('register.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Calendar Events
    if session['role'] == 'coach':
        c.execute("SELECT * FROM events WHERE team_id = ? OR creator_id = ?", 
                 (session['team_id'], session['user_id']))
    else:
        c.execute("SELECT * FROM events WHERE team_id = ? OR creator_id = ?", 
                 (session['team_id'], session['user_id']))
    events = c.fetchall()
    
    # To-Do List (events for today)
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute("SELECT * FROM events WHERE (team_id = ? OR creator_id = ?) AND date = ?", 
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
        event_type = request.form['type']
        notes = request.form['notes']
        required_items = request.form.get('required_items', '') if session['role'] == 'coach' else ''
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        team_id = session['team_id'] if event_type == 'team' and session['role'] == 'coach' else None
        c.execute("INSERT INTO events (date, time, location, type, notes, required_items, creator_id, team_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
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
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM events WHERE event_id = ?", (event_id,))
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
        c.execute("UPDATE events SET date = ?, time = ?, location = ?, notes = ?, required_items = ? WHERE event_id = ?", 
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
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO attendance (event_id, user_id, status) VALUES (?, ?, ?)", 
             (event_id, session['user_id'], status))
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
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO fitness_feedback (event_id, user_id, fatigue_level, mental_state, notes) VALUES (?, ?, ?, ?, ?)", 
                 (event_id, session['user_id'], fatigue, mental, notes))
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
    event_id = request.form.get('event_id', None)
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO messages (sender_id, team_id, content, timestamp, event_id) VALUES (?, ?, ?, ?, ?)", 
             (session['user_id'], session['team_id'], content, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), event_id))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

# Toggle Notifications
@app.route('/toggle_notifications', methods=['POST'])
def toggle_notifications():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    pref = 1 if request.form.get('notifications') == 'on' else 0
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("UPDATE users SET notification_preference = ? WHERE user_id = ?", (pref, session['user_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)