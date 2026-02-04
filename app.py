from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'cinemapulse-2026-movies'

def init_db():
    conn = sqlite3.connect('cinemapulse.db')
    c = conn.cursor()
    
    c.execute('DROP TABLE IF EXISTS feedbacks')
    c.execute('DROP TABLE IF EXISTS movies')
    c.execute('DROP TABLE IF EXISTS users')
    
    c.execute('''CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        user_type TEXT DEFAULT 'user'
    )''')
    
    c.execute('''CREATE TABLE movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        average_rating REAL DEFAULT 0.0,
        total_reviews INTEGER DEFAULT 0
    )''')
    
    c.execute('''CREATE TABLE feedbacks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        movie_id INTEGER NOT NULL,
        rating INTEGER NOT NULL,
        comments TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 🔥 12 HOTTEST 2026 MOVIES
    movies = [
        ("Parashakthi", "Sivakarthikeyan's historical action epic about brothers clashing during Tamil Nadu's 1965 Anti-Hindi protests, directed by Sudha Kongara.",),
        ("Lara ", " Ashok Kumar hunts a mysterious killer amid corruption—pure detective noir suspense."),
        ("Eleven", "Skilled officer tackles brutal serial killings with psychological twists."),
        ("Kaantha ", "1950s Madras mystery blending social drama and hidden crimes."),
        ("Stephen", "Psychiatrist unravels a killer's mind in a chilling evaluation gone wrong."),
        ("Show Time", "Naveen Chandra in a tense crime unraveling full of betrayals."),
        ("Vikram", " Kamal Haasan as a brooding cop in gritty action—noir, echoing Batman's intensity "),
        ("Blackmail", "GV Prakash in a drama-thriller of deceit and dark secrets."),
        ("Maargan", "Vijay Antony's crime-mystery with supernatural detective edges."),
        ("Ace ", "Vijay Sethupathi as a crime-busting anti-hero in high-stakes action-noir."),
        ("Narivettai ", "Tovino Thomas in a revenge-fueled crime probe."),
        ("Indra", " Vasanth Ravi's suspenseful pursuit through betrayal webs."),
        ("Sleepwalker","Psychological thriller about a mother caught in grief and blurred reality after her daughters loss."),
        ("28 Years Later: The Bone Temple","A post-apocalyptic survival horror sequel that follows humanity struggle to survive decades after a devastating global outbreak."),
        ("Return to Silent Hill","Horror film based on the classic video game franchise Silent Hill with atmospheric thrills.")
    ]
    c.executemany("INSERT INTO movies (title, description) VALUES (?, ?)", movies)
    
    c.execute("INSERT OR REPLACE INTO users VALUES (1, 'Admin', 'admin@cinemapulse.com', 'admin123', 'admin')")
    c.execute("INSERT OR REPLACE INTO users VALUES (2, 'User', 'user@cinemapulse.com', 'user123', 'user')")
    
    conn.commit()
    conn.close()
    print("✅ 15 HOT 2026 MOVIES LOADED!")
    print("👤 USER: user@cinemapulse.com / user123")
    print("🔧 ADMIN: admin@cinemapulse.com / admin123")

def get_db():
    conn = sqlite3.connect('cinemapulse.db')
    conn.row_factory = sqlite3.Row
    return conn

def update_movie_stats(movie_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT SUM(rating), COUNT(*) FROM feedbacks WHERE movie_id=?", (movie_id,))
    result = c.fetchone()
    total, count = result[0] or 0, result[1] or 0
    avg = round(total/count, 1) if count else 0.0
    c.execute("UPDATE movies SET average_rating=?, total_reviews=? WHERE id=?", (avg, count, movie_id))
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password'].strip()
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE email=? AND password=?', (email, password)).fetchone()
        conn.close()
        if user:
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['user_type'] = user['user_type']
            flash(f'✅ Welcome {user["username"]}!')
            return redirect(url_for('about'))
        flash('❌ Invalid credentials!')
    return render_template('login.html')

@app.route('/about')
def about():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('about.html')

@app.route('/home')
def home():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db()
    movies = conn.execute('SELECT * FROM movies ORDER BY title ASC').fetchall()
    conn.close()
    return render_template('home.html', movies=movies)

@app.route('/feedback/<int:movie_id>', methods=['GET', 'POST'])
def feedback(movie_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db()
    movie = conn.execute('SELECT * FROM movies WHERE id=?', (movie_id,)).fetchone()
    if request.method == 'POST':
        c = conn.cursor()
        c.execute('''INSERT INTO feedbacks (username, email, movie_id, rating, comments) 
                    VALUES (?, ?, ?, ?, ?)''', 
                    (request.form['username'], request.form['email'], movie_id, 
                     int(request.form['rating']), request.form['comments']))
        conn.commit()
        update_movie_stats(movie_id)
        conn.close()
        return redirect(url_for('thankyou', movie_id=movie_id))
    conn.close()
    return render_template('feedback.html', movie=movie)

@app.route('/thankyou/<int:movie_id>')
def thankyou(movie_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db()
    movie = conn.execute('SELECT * FROM movies WHERE id=?', (movie_id,)).fetchone()
    conn.close()
    return render_template('thankyou.html', movie=movie)

@app.route('/admin')
def admin_panel():
    if session.get('user_type') != 'admin': return redirect(url_for('login'))
    conn = get_db()
    feedbacks = conn.execute('''SELECT f.*, m.title as movie_title 
                               FROM feedbacks f JOIN movies m ON f.movie_id = m.id 
                               ORDER BY f.created_at DESC''').fetchall()
    conn.close()
    return render_template('admin.html', feedbacks=feedbacks)

@app.route('/logout')
def logout():
    session.clear()
    flash('👋 Logged out!')
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    print("\n🚀 http://localhost:5000")
    app.run(debug=True)












