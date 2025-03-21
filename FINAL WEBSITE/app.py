from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a strong secret key

# Path to the SQLite database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "registrations.db")

# Initialize the SQLite database and create the registrations table if it doesn't exist
def init_db():
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS registrations (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          name TEXT NOT NULL,
                          email TEXT NOT NULL UNIQUE,
                          address TEXT NOT NULL,
                          phone TEXT NOT NULL,
                          method TEXT NOT NULL)''')
        conn.commit()

# Route for the registration form
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    address = data.get('address')
    phone = data.get('phone')
    method = data.get('method')
    
    # Check for unique email
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM registrations WHERE email = ?", (email,))
        if cursor.fetchone():
            return jsonify({"message": "Email already registered. Please use a different email."}), 409

        # Insert the new registration
        cursor.execute("INSERT INTO registrations (name, email, address, phone, method) VALUES (?, ?, ?, ?, ?)", 
                       (name, email, address, phone, method))
        conn.commit()  # Explicitly commit the transaction

    return jsonify({"message": "Registration successful."}), 201

# Route to display registrations
@app.route('/registrations')
def registrations():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.row_factory = sqlite3.Row  # Make rows behave like dictionaries
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM registrations")
        registrations = cursor.fetchall()
    
    return render_template('registrations.html', registrations=registrations)


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        # Use a hashed password here; replace with `generate_password_hash('your_password')` for actual security
        stored_password_hash = generate_password_hash('your_password')
        if check_password_hash(stored_password_hash, password):
            session['logged_in'] = True
            return redirect(url_for('registrations'))
        else:
            flash("Incorrect password. Please try again.")
    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('logged_in', None)  # Remove the session variable
    return redirect(url_for('login'))

# Home route
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    init_db()  # Initialize the database when the app starts
    app.run(debug=True, host='0.0.0.0')
